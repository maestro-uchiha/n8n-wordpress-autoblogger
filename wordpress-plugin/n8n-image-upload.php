<?php
/**
 * Plugin Name: n8n Autoblogger Helper
 * Description: REST API endpoints for n8n autoblogging - image uploads, SEO meta, and category management
 * Version: 1.2
 * Author: Autoblogger
 */

if (!defined('ABSPATH')) exit;

add_action('rest_api_init', function() {
    register_rest_route('n8n/v1', '/upload-image', [
        'methods' => 'POST',
        'callback' => 'n8n_handle_image_upload',
        'permission_callback' => function($request) {
            return current_user_can('upload_files');
        }
    ]);
    
    register_rest_route('n8n/v1', '/sideload-image', [
        'methods' => 'POST',
        'callback' => 'n8n_handle_image_sideload',
        'permission_callback' => function($request) {
            return current_user_can('upload_files');
        }
    ]);
    
    // v1.1: SEO meta update endpoint
    register_rest_route('n8n/v1', '/update-seo-meta', [
        'methods' => 'POST',
        'callback' => 'n8n_handle_seo_meta_update',
        'permission_callback' => function($request) {
            return current_user_can('edit_posts');
        }
    ]);
    
    // v1.2: Category creation endpoint (bypasses REST API permission issues)
    register_rest_route('n8n/v1', '/create-category', [
        'methods' => 'POST',
        'callback' => 'n8n_handle_create_category',
        'permission_callback' => function($request) {
            return current_user_can('edit_posts');
        }
    ]);
});

/**
 * Upload image from base64 data
 * POST /wp-json/n8n/v1/upload-image
 * Body: { "base64": "...", "filename": "image.png", "mime_type": "image/png", "alt_text": "..." }
 */
function n8n_handle_image_upload($request) {
    $params = $request->get_json_params();
    
    $base64 = $params['base64'] ?? '';
    $filename = sanitize_file_name($params['filename'] ?? 'image-' . time() . '.png');
    $mime_type = $params['mime_type'] ?? 'image/png';
    $alt_text = sanitize_text_field($params['alt_text'] ?? '');
    $title = sanitize_text_field($params['title'] ?? $filename);
    
    if (empty($base64)) {
        return new WP_Error('no_base64', 'Base64 data is required', ['status' => 400]);
    }
    
    // Remove data URL prefix if present
    if (strpos($base64, 'base64,') !== false) {
        $base64 = explode('base64,', $base64)[1];
    }
    
    // Decode base64
    $image_data = base64_decode($base64);
    if ($image_data === false) {
        return new WP_Error('decode_failed', 'Failed to decode base64 data', ['status' => 400]);
    }
    
    // Validate image
    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $detected_mime = $finfo->buffer($image_data);
    if (!in_array($detected_mime, ['image/jpeg', 'image/png', 'image/gif', 'image/webp'])) {
        return new WP_Error('invalid_image', 'Invalid image type: ' . $detected_mime, ['status' => 400]);
    }
    
    // Get upload directory
    $upload_dir = wp_upload_dir();
    if ($upload_dir['error']) {
        return new WP_Error('upload_dir_error', $upload_dir['error'], ['status' => 500]);
    }
    
    // Generate unique filename
    $ext = pathinfo($filename, PATHINFO_EXTENSION);
    if (!$ext) {
        $ext = ($detected_mime === 'image/png') ? 'png' : (($detected_mime === 'image/webp') ? 'webp' : 'jpg');
        $filename .= '.' . $ext;
    }
    $unique_filename = wp_unique_filename($upload_dir['path'], $filename);
    $file_path = $upload_dir['path'] . '/' . $unique_filename;
    
    // Write file
    $bytes_written = file_put_contents($file_path, $image_data);
    if ($bytes_written === false) {
        return new WP_Error('write_failed', 'Failed to write image file', ['status' => 500]);
    }
    
    // Create attachment
    $attachment = [
        'post_mime_type' => $detected_mime,
        'post_title' => $title,
        'post_content' => '',
        'post_status' => 'inherit'
    ];
    
    $attachment_id = wp_insert_attachment($attachment, $file_path);
    if (is_wp_error($attachment_id)) {
        @unlink($file_path);
        return $attachment_id;
    }
    
    // Generate metadata
    require_once(ABSPATH . 'wp-admin/includes/image.php');
    $metadata = wp_generate_attachment_metadata($attachment_id, $file_path);
    wp_update_attachment_metadata($attachment_id, $metadata);
    
    // Set alt text
    if ($alt_text) {
        update_post_meta($attachment_id, '_wp_attachment_image_alt', $alt_text);
    }
    
    return [
        'success' => true,
        'id' => $attachment_id,
        'url' => wp_get_attachment_url($attachment_id),
        'source_url' => wp_get_attachment_url($attachment_id),
        'filename' => $unique_filename,
        'size' => $bytes_written
    ];
}

/**
 * Sideload image from URL (WordPress downloads it)
 * POST /wp-json/n8n/v1/sideload-image
 * Body: { "url": "https://...", "filename": "image.png", "alt_text": "..." }
 */
function n8n_handle_image_sideload($request) {
    $params = $request->get_json_params();
    
    $url = esc_url_raw($params['url'] ?? '');
    $filename = sanitize_file_name($params['filename'] ?? '');
    $alt_text = sanitize_text_field($params['alt_text'] ?? '');
    $title = sanitize_text_field($params['title'] ?? $filename);
    
    if (empty($url)) {
        return new WP_Error('no_url', 'Image URL is required', ['status' => 400]);
    }
    
    require_once(ABSPATH . 'wp-admin/includes/media.php');
    require_once(ABSPATH . 'wp-admin/includes/file.php');
    require_once(ABSPATH . 'wp-admin/includes/image.php');
    
    // Download file to temp
    $tmp = download_url($url, 30);
    if (is_wp_error($tmp)) {
        return new WP_Error('download_failed', 'Failed to download: ' . $tmp->get_error_message(), ['status' => 500]);
    }
    
    // Prepare file array
    if (!$filename) {
        $filename = basename(parse_url($url, PHP_URL_PATH));
    }
    
    $file_array = [
        'name' => $filename,
        'tmp_name' => $tmp
    ];
    
    // Sideload into media library
    $attachment_id = media_handle_sideload($file_array, 0, $title);
    
    // Clean up temp file
    @unlink($tmp);
    
    if (is_wp_error($attachment_id)) {
        return $attachment_id;
    }
    
    // Set alt text
    if ($alt_text) {
        update_post_meta($attachment_id, '_wp_attachment_image_alt', $alt_text);
    }
    
    return [
        'success' => true,
        'id' => $attachment_id,
        'url' => wp_get_attachment_url($attachment_id),
        'source_url' => wp_get_attachment_url($attachment_id),
        'filename' => $filename
    ];
}

/**
 * Update SEO meta for Yoast and RankMath
 * POST /wp-json/n8n/v1/update-seo-meta
 * Body: { "post_id": 123, "focus_keyphrase": "...", "meta_description": "...", "seo_title": "..." }
 */
function n8n_handle_seo_meta_update($request) {
    $params = $request->get_json_params();
    
    $post_id = intval($params['post_id'] ?? 0);
    $focus_keyphrase = sanitize_text_field($params['focus_keyphrase'] ?? '');
    $meta_description = sanitize_text_field($params['meta_description'] ?? '');
    $seo_title = sanitize_text_field($params['seo_title'] ?? '');
    
    if (!$post_id || !get_post($post_id)) {
        return new WP_Error('invalid_post', 'Invalid post ID', ['status' => 400]);
    }
    
    $updated = [];
    
    // Detect which SEO plugin is active
    $has_yoast = defined('WPSEO_VERSION') || class_exists('WPSEO_Meta');
    $has_rankmath = class_exists('RankMath') || defined('RANK_MATH_VERSION');
    
    // Update Yoast SEO meta
    if ($has_yoast) {
        if ($focus_keyphrase) {
            update_post_meta($post_id, '_yoast_wpseo_focuskw', $focus_keyphrase);
            $updated['yoast_focus_keyword'] = true;
        }
        if ($meta_description) {
            update_post_meta($post_id, '_yoast_wpseo_metadesc', $meta_description);
            $updated['yoast_meta_description'] = true;
        }
        if ($seo_title) {
            update_post_meta($post_id, '_yoast_wpseo_title', $seo_title);
            $updated['yoast_title'] = true;
        }
    }
    
    // Update RankMath SEO meta
    if ($has_rankmath) {
        if ($focus_keyphrase) {
            update_post_meta($post_id, 'rank_math_focus_keyword', $focus_keyphrase);
            $updated['rankmath_focus_keyword'] = true;
        }
        if ($meta_description) {
            update_post_meta($post_id, 'rank_math_description', $meta_description);
            $updated['rankmath_description'] = true;
        }
        if ($seo_title) {
            update_post_meta($post_id, 'rank_math_title', $seo_title);
            $updated['rankmath_title'] = true;
        }
        
        // RankMath also stores robots meta - set to index
        update_post_meta($post_id, 'rank_math_robots', ['index']);
    }
    
    // If no SEO plugin detected, still store the meta for later
    if (!$has_yoast && !$has_rankmath) {
        if ($focus_keyphrase) {
            update_post_meta($post_id, '_n8n_focus_keyphrase', $focus_keyphrase);
            $updated['n8n_focus_keyphrase'] = true;
        }
        if ($meta_description) {
            update_post_meta($post_id, '_n8n_meta_description', $meta_description);
            $updated['n8n_meta_description'] = true;
        }
    }
    
    return [
        'success' => true,
        'post_id' => $post_id,
        'seo_plugins' => [
            'yoast' => $has_yoast,
            'rankmath' => $has_rankmath
        ],
        'updated' => $updated
    ];
}

/**
 * Create a category (bypasses REST API permission issues)
 * POST /wp-json/n8n/v1/create-category
 * Body: { "name": "Category Name", "slug": "category-slug", "parent": 0 }
 */
function n8n_handle_create_category($request) {
    $params = $request->get_json_params();
    
    $name = sanitize_text_field($params['name'] ?? '');
    $slug = sanitize_title($params['slug'] ?? $name);
    $parent = intval($params['parent'] ?? 0);
    
    if (empty($name)) {
        return new WP_Error('no_name', 'Category name is required', ['status' => 400]);
    }
    
    // Check if category already exists by name or slug
    $existing = get_term_by('name', $name, 'category');
    if (!$existing) {
        $existing = get_term_by('slug', $slug, 'category');
    }
    
    if ($existing) {
        return [
            'success' => true,
            'id' => $existing->term_id,
            'name' => $existing->name,
            'slug' => $existing->slug,
            'created' => false,
            'message' => 'Category already exists'
        ];
    }
    
    // Create the category
    $result = wp_insert_term($name, 'category', [
        'slug' => $slug,
        'parent' => $parent
    ]);
    
    if (is_wp_error($result)) {
        return new WP_Error('create_failed', $result->get_error_message(), ['status' => 500]);
    }
    
    return [
        'success' => true,
        'id' => $result['term_id'],
        'name' => $name,
        'slug' => $slug,
        'created' => true
    ];
}
