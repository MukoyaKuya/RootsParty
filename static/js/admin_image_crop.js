/**
 * Admin Image Crop Tool
 * Initializes Jcrop on image previews after upload
 */
(function($) {
    'use strict';
    
    // Wait for Jcrop to be available
    function waitForJcrop(callback, maxAttempts) {
        maxAttempts = maxAttempts || 50;
        var attempts = 0;
        
        function check() {
            if (typeof $.fn.Jcrop !== 'undefined') {
                callback();
            } else if (attempts < maxAttempts) {
                attempts++;
                setTimeout(check, 100);
            } else {
                console.error('Jcrop library failed to load');
            }
        }
        check();
    }
    
    function initImageCrop($container) {
        var $input = $container.find('input[type="file"]');
        var $previewContainer = $container.find('.image-preview-container');
        var $previewImg = $previewContainer.find('img');
        var cropWidth = parseInt($container.data('crop-width')) || 800;
        var cropHeight = parseInt($container.data('crop-height')) || 450;
        
        // Parse crop ratio - can be a number or "width/height" string
        var cropRatioData = $container.data('crop-ratio');
        var cropRatio;
        if (typeof cropRatioData === 'string' && cropRatioData.indexOf('/') !== -1) {
            // Parse "800/450" format
            var parts = cropRatioData.split('/');
            cropRatio = parseFloat(parts[0]) / parseFloat(parts[1]);
        } else {
            cropRatio = parseFloat(cropRatioData) || (cropWidth / cropHeight);
        }
        var jcropApi = null;
        var fieldId = $input.attr('id');
        
        // Store actual image dimensions for coordinate scaling
        var actualImageWidth = null;
        var actualImageHeight = null;
        
        function updateCropCoords(c) {
            // When trueSize is set, Jcrop returns coordinates in actual image size
            // So we can use them directly
            if (!c || c.w <= 0 || c.h <= 0) {
                return; // Invalid coordinates
            }
            
            // Scale coordinates from displayed size to actual image size
            if (actualImageWidth && actualImageHeight) {
                var displayedWidth = $previewImg.width() || $previewImg.outerWidth();
                var displayedHeight = $previewImg.height() || $previewImg.outerHeight();
                
                // Only scale if displayed size differs from actual size
                if (displayedWidth && displayedHeight && 
                    (Math.abs(displayedWidth - actualImageWidth) > 1 || 
                     Math.abs(displayedHeight - actualImageHeight) > 1)) {
                    var scaleX = actualImageWidth / displayedWidth;
                    var scaleY = actualImageHeight / displayedHeight;
                    
                    var coords = {
                        x: c.x * scaleX,
                        y: c.y * scaleY,
                        w: c.w * scaleX,
                        h: c.h * scaleY
                    };
                    
                    $('#' + fieldId + '_crop_x').val(Math.round(coords.x));
                    $('#' + fieldId + '_crop_y').val(Math.round(coords.y));
                    $('#' + fieldId + '_crop_w').val(Math.round(coords.w));
                    $('#' + fieldId + '_crop_h').val(Math.round(coords.h));
                } else {
                    // Same size, use coordinates directly
                    $('#' + fieldId + '_crop_x').val(Math.round(c.x));
                    $('#' + fieldId + '_crop_y').val(Math.round(c.y));
                    $('#' + fieldId + '_crop_w').val(Math.round(c.w));
                    $('#' + fieldId + '_crop_h').val(Math.round(c.h));
                }
            } else {
                // Fallback: use coordinates as-is
                $('#' + fieldId + '_crop_x').val(Math.round(c.x));
                $('#' + fieldId + '_crop_y').val(Math.round(c.y));
                $('#' + fieldId + '_crop_w').val(Math.round(c.w));
                $('#' + fieldId + '_crop_h').val(Math.round(c.h));
            }
        }
        
        function initCrop(imageSrc) {
            // Destroy existing Jcrop
            if (jcropApi) {
                try {
                    jcropApi.destroy();
                } catch(e) {
                    console.log('Error destroying Jcrop:', e);
                }
                jcropApi = null;
            }
            
            // Set image source and ensure it's visible
            $previewImg.attr('src', imageSrc);
            $previewImg.css({
                'max-width': '800px',
                'width': 'auto',
                'height': 'auto',
                'display': 'block',
                'visibility': 'visible',
                'opacity': '1'
            });
            $previewContainer.css({
                'display': 'block',
                'visibility': 'visible'
            }).show();
            
            // Function to initialize Jcrop with proper dimensions
            function initializeJcrop() {
                waitForJcrop(function() {
                    // Get actual image dimensions
                    var imgElement = $previewImg[0];
                    
                    // Wait for image to have dimensions
                    var getDimensions = function(attempt) {
                        attempt = attempt || 0;
                        if (attempt > 20) {
                            console.error('Failed to get image dimensions after 20 attempts');
                            return;
                        }
                        
                        // Force image to be visible and get its displayed dimensions
                        // Jcrop works with displayed dimensions, not natural dimensions
                        var imgWidth = $previewImg.outerWidth() || $previewImg.width() || imgElement.offsetWidth;
                        var imgHeight = $previewImg.outerHeight() || $previewImg.height() || imgElement.offsetHeight;
                        
                        // If dimensions aren't available yet, retry
                        if (!imgWidth || !imgHeight || imgWidth < 50 || imgHeight < 50) {
                            setTimeout(function() {
                                getDimensions(attempt + 1);
                            }, 100);
                            return;
                        }
                        
                        console.log('Image dimensions:', imgWidth, 'x', imgHeight);
                        
                        // Calculate initial crop size (centered, maintaining aspect ratio)
                        // Use 60% of image dimensions for initial crop
                        var initWidth = Math.max(150, Math.min(imgWidth * 0.6, imgWidth - 20));
                        var initHeight = initWidth / cropRatio;
                        
                        // If height exceeds image, adjust
                        if (initHeight > imgHeight * 0.6) {
                            initHeight = Math.max(150, imgHeight * 0.6);
                            initWidth = initHeight * cropRatio;
                        }
                        
                        // Ensure crop fits within image bounds
                        if (initWidth > imgWidth - 10) {
                            initWidth = Math.max(150, imgWidth - 10);
                            initHeight = initWidth / cropRatio;
                        }
                        if (initHeight > imgHeight - 10) {
                            initHeight = Math.max(150, imgHeight - 10);
                            initWidth = initHeight * cropRatio;
                        }
                        
                        // Center the crop box
                        var initX = Math.max(10, (imgWidth - initWidth) / 2);
                        var initY = Math.max(10, (imgHeight - initHeight) / 2);
                        
                        // Ensure coordinates are valid
                        initX = Math.max(0, Math.min(initX, imgWidth - initWidth - 10));
                        initY = Math.max(0, Math.min(initY, imgHeight - initHeight - 10));
                        
                        console.log('Initial crop box:', initX, initY, initWidth, initHeight);
                        
                        // Destroy existing Jcrop if any
                        if (jcropApi) {
                            try {
                                jcropApi.destroy();
                            } catch(e) {
                                console.log('Error destroying Jcrop:', e);
                            }
                            jcropApi = null;
                        }
                        
                        // Remove any existing Jcrop elements
                        $previewImg.siblings('.jcrop-holder').remove();
                        $previewImg.parent().find('.jcrop-holder').remove();
                        $previewImg.parent().parent().find('.jcrop-holder').remove();
                        
                        // Ensure image is visible and has proper styling
                        $previewImg.css({
                            'display': 'block',
                            'visibility': 'visible',
                            'opacity': '1'
                        });
                        
                        // Initialize Jcrop with proper dimensions
                        try {
                            // Ensure image is ready and visible
                            $previewImg.css({
                                'display': 'block',
                                'visibility': 'visible',
                                'opacity': '1',
                                'position': 'relative',
                                'z-index': '1'
                            });
                            
                            $previewImg.Jcrop({
                                aspectRatio: cropRatio,
                                setSelect: [initX, initY, initX + initWidth, initY + initHeight],
                                onSelect: updateCropCoords,
                                onChange: updateCropCoords,
                                bgColor: 'black',
                                bgOpacity: 0.4,
                                minSize: [100, 100 / cropRatio],
                                trueSize: [actualImageWidth, actualImageHeight],
                                allowSelect: true,
                                allowMove: true,
                                allowResize: true
                            }, function() {
                                jcropApi = this;
                                console.log('Jcrop initialized successfully');
                                console.log('Jcrop API:', this);
                                
                                // Update coordinates with initial selection
                                try {
                                    var coords = this.tellSelect();
                                    console.log('Initial crop coordinates:', coords);
                                    if (coords && coords.w > 0 && coords.h > 0) {
                                        updateCropCoords(coords);
                                    }
                                } catch(e) {
                                    console.error('Error getting initial crop coordinates:', e);
                                }
                            });
                        } catch(e) {
                            console.error('Error initializing Jcrop:', e);
                            console.error('Error details:', e.message, e.stack);
                        }
                    };
                    
                    // Small delay to ensure image is rendered
                    setTimeout(function() {
                        getDimensions();
                    }, 100);
                });
            }
            
            // Wait for image to load
            $previewImg.off('load.crop').on('load.crop', function() {
                // Small delay to ensure dimensions are available
                setTimeout(initializeJcrop, 50);
            });
            
            // Trigger load if image is already loaded
            if ($previewImg[0].complete && $previewImg[0].naturalWidth > 0) {
                setTimeout(function() {
                    $previewImg.trigger('load.crop');
                }, 100);
            }
        }
        
        // Handle file selection
        $input.on('change', function(e) {
            if (this.files && this.files[0]) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    initCrop(e.target.result);
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
        
        // Initialize with existing image if present
        var existingImg = $container.find('.existing-image-container img');
        if (existingImg.length > 0 && existingImg.attr('src')) {
            initCrop(existingImg.attr('src'));
        }
    }
    
    // Initialize on page load
    $(document).ready(function() {
        $('.image-crop-widget').each(function() {
            initImageCrop($(this));
        });
    });
    
    // Re-initialize for dynamically added widgets
    if (typeof MutationObserver !== 'undefined') {
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                $(mutation.addedNodes).find('.image-crop-widget').each(function() {
                    initImageCrop($(this));
                });
            });
        });
        
        $(document).ready(function() {
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    }
})(django.jQuery || jQuery);
