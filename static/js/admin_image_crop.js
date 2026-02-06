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
            if (typeof $.fn.Jcrop !== 'undefined' && typeof $.fn.Jcrop === 'function') {
                console.log('Jcrop is available');
                callback();
            } else if (attempts < maxAttempts) {
                attempts++;
                if (attempts % 10 === 0) {
                    console.log('Waiting for Jcrop... attempt', attempts);
                }
                setTimeout(check, 100);
            } else {
                console.error('Jcrop library failed to load after', maxAttempts, 'attempts');
                console.error('jQuery version:', $.fn.jquery);
                console.error('$.fn.Jcrop:', typeof $.fn.Jcrop);
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
            if (!c || c.w <= 0 || c.h <= 0) {
                console.warn('Invalid crop coordinates:', c);
                return;
            }
            
            // Always scale coordinates from displayed size to actual image size
            // This ensures accurate cropping regardless of how the image is displayed
            if (actualImageWidth && actualImageHeight && actualImageWidth > 0 && actualImageHeight > 0) {
                var displayedWidth = $previewImg.width() || $previewImg.outerWidth();
                var displayedHeight = $previewImg.height() || $previewImg.outerHeight();
                
                if (displayedWidth && displayedHeight && displayedWidth > 0 && displayedHeight > 0) {
                    var scaleX = actualImageWidth / displayedWidth;
                    var scaleY = actualImageHeight / displayedHeight;
                    
                    var coords = {
                        x: Math.round(c.x * scaleX),
                        y: Math.round(c.y * scaleY),
                        w: Math.round(c.w * scaleX),
                        h: Math.round(c.h * scaleY)
                    };
                    
                    $('#' + fieldId + '_crop_x').val(coords.x);
                    $('#' + fieldId + '_crop_y').val(coords.y);
                    $('#' + fieldId + '_crop_w').val(coords.w);
                    $('#' + fieldId + '_crop_h').val(coords.h);
                } else {
                    // Fallback: use coordinates as-is if we can't get displayed size
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
            console.log('=== initCrop called with imageSrc ===');
            
            // Destroy existing Jcrop
            if (jcropApi) {
                try {
                    jcropApi.destroy();
                } catch(e) {
                    console.log('Error destroying Jcrop:', e);
                }
                jcropApi = null;
            }
            
            // STEP 1: Show the container FIRST (before setting image src)
            $previewContainer.css({
                'display': 'block',
                'visibility': 'visible'
            }).show();
            $previewContainer.attr('style', 'display: block !important; visibility: visible !important; margin-top: 15px;');
            console.log('Container shown');
            
            // STEP 2: Set image source
            $previewImg.attr('src', imageSrc);
            console.log('Image src set');
            
            // STEP 3: Force image to be visible immediately with !important
            // Remove any existing style and set fresh
            $previewImg.attr('style', 'display: block !important; visibility: visible !important; opacity: 1 !important; pointer-events: auto !important; max-width: 800px; width: auto; height: auto; cursor: crosshair !important;');
            
            // Also set via CSS
            $previewImg.css({
                'display': 'block',
                'visibility': 'visible',
                'opacity': '1',
                'pointer-events': 'auto',
                'max-width': '800px',
                'width': 'auto',
                'height': 'auto'
            });
            
            console.log('Image visibility forced');
            console.log('Image element:', $previewImg[0]);
            console.log('Image inline style:', $previewImg.attr('style'));
            console.log('Image computed display:', $previewImg.css('display'));
            console.log('Image computed visibility:', $previewImg.css('visibility'));
            console.log('Image is visible?', $previewImg.is(':visible'));
            
            // Function to initialize Jcrop with proper dimensions
            function initializeJcrop() {
                console.log('=== initializeJcrop called ===');
                
                // CRITICAL: Verify image is visible before proceeding
                if (!$previewImg.is(':visible')) {
                    console.error('Image is NOT visible! Forcing visibility again...');
                    $previewImg.attr('style', 'display: block !important; visibility: visible !important; opacity: 1 !important; pointer-events: auto !important; max-width: 800px; width: auto; height: auto; cursor: crosshair !important;');
                    $previewContainer.show();
                    
                    // Wait a bit and retry
                    setTimeout(initializeJcrop, 200);
                    return;
                }
                
                waitForJcrop(function() {
                    console.log('Jcrop library is available, proceeding...');
                    
                    // Get actual image dimensions
                    var imgElement = $previewImg[0];
                    
                    // Store coordinates in outer scope
                    var initX, initY, initWidth, initHeight, imgWidth, imgHeight;
                    
                    // Wait for image to have dimensions
                    var getDimensions = function(attempt) {
                        attempt = attempt || 0;
                        if (attempt > 20) {
                            console.error('Failed to get image dimensions after 20 attempts');
                            return;
                        }
                        
                        // Double-check visibility
                        if (!$previewImg.is(':visible')) {
                            console.error('Image became hidden during dimension check!');
                            $previewImg.attr('style', 'display: block !important; visibility: visible !important;');
                            setTimeout(function() { getDimensions(attempt + 1); }, 100);
                            return;
                        }
                        
                        // Force image to be visible and get its displayed dimensions
                        // Jcrop works with displayed dimensions, not natural dimensions
                        imgWidth = $previewImg.outerWidth() || $previewImg.width() || imgElement.offsetWidth;
                        imgHeight = $previewImg.outerHeight() || $previewImg.height() || imgElement.offsetHeight;
                        
                        // If dimensions aren't available yet, retry
                        if (!imgWidth || !imgHeight || imgWidth < 50 || imgHeight < 50) {
                            console.log('Dimensions not ready, retrying...', imgWidth, imgHeight);
                            setTimeout(function() {
                                getDimensions(attempt + 1);
                            }, 100);
                            return;
                        }
                        
                        console.log('Image dimensions obtained:', imgWidth, 'x', imgHeight);
                        
                        // Calculate initial crop size (centered, maintaining aspect ratio)
                        // Use 80% of image dimensions for initial crop, but ensure minimum size
                        var minCropSize = 200;
                        initWidth = Math.max(minCropSize, Math.min(imgWidth * 0.8, imgWidth - 20));
                        initHeight = initWidth / cropRatio;
                        
                        // If height exceeds image, adjust based on height
                        if (initHeight > imgHeight - 20) {
                            initHeight = Math.max(minCropSize, imgHeight - 20);
                            initWidth = initHeight * cropRatio;
                            
                            // Re-check width
                            if (initWidth > imgWidth - 20) {
                                initWidth = Math.max(minCropSize, imgWidth - 20);
                                initHeight = initWidth / cropRatio;
                            }
                        }
                        
                        // Final validation - ensure crop fits within image
                        if (initWidth >= imgWidth) {
                            initWidth = Math.max(minCropSize, imgWidth - 20);
                            initHeight = initWidth / cropRatio;
                        }
                        if (initHeight >= imgHeight) {
                            initHeight = Math.max(minCropSize, imgHeight - 20);
                            initWidth = initHeight * cropRatio;
                        }
                        
                        // Center the crop box
                        initX = Math.max(0, Math.floor((imgWidth - initWidth) / 2));
                        initY = Math.max(0, Math.floor((imgHeight - initHeight) / 2));
                        
                        // Final bounds check
                        if (initX + initWidth > imgWidth) {
                            initX = Math.max(0, imgWidth - initWidth);
                        }
                        if (initY + initHeight > imgHeight) {
                            initY = Math.max(0, imgHeight - initHeight);
                        }
                        
                        // Ensure all values are positive integers
                        initX = Math.max(0, Math.floor(initX));
                        initY = Math.max(0, Math.floor(initY));
                        initWidth = Math.max(minCropSize, Math.floor(initWidth));
                        initHeight = Math.max(minCropSize, Math.floor(initHeight));
                        
                        // Final validation
                        if (initX + initWidth > imgWidth || initY + initHeight > imgHeight || 
                            initWidth <= 0 || initHeight <= 0 || initX < 0 || initY < 0) {
                            console.error('Invalid crop coordinates calculated:', {
                                x: initX, y: initY, w: initWidth, h: initHeight,
                                imgW: imgWidth, imgH: imgHeight
                            });
                            // Fallback to safe defaults
                            initWidth = Math.min(400, imgWidth - 20);
                            initHeight = Math.floor(initWidth / cropRatio);
                            if (initHeight > imgHeight - 20) {
                                initHeight = imgHeight - 20;
                                initWidth = Math.floor(initHeight * cropRatio);
                            }
                            initX = Math.max(0, Math.floor((imgWidth - initWidth) / 2));
                            initY = Math.max(0, Math.floor((imgHeight - initHeight) / 2));
                        }
                        
                        console.log('Initial crop box calculated:', {
                            x: initX, y: initY, w: initWidth, h: initHeight,
                            x2: initX + initWidth, y2: initY + initHeight,
                            imgW: imgWidth, imgH: imgHeight
                        });
                        
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
                        
                        // CRITICAL: Force image to be visible RIGHT BEFORE initializing Jcrop
                        // Check current state
                        var currentDisplay = $previewImg.css('display');
                        var currentVisibility = $previewImg.css('visibility');
                        console.log('Before forcing visibility - display:', currentDisplay, 'visibility:', currentVisibility);
                        
                        // Force visibility with inline style (strongest) - use !important
                        $previewImg.attr('style', 'display: block !important; visibility: visible !important; opacity: 1 !important; pointer-events: auto !important; max-width: 800px; width: auto; height: auto; cursor: crosshair !important;');
                        
                        // Also ensure container is visible
                        $previewContainer.attr('style', 'display: block !important; visibility: visible !important; pointer-events: auto !important; margin-top: 15px;');
                        $previewContainer.show();
                        
                        // Verify visibility
                        var finalDisplay = $previewImg.css('display');
                        var finalVisibility = $previewImg.css('visibility');
                        var isVisible = $previewImg.is(':visible');
                        console.log('After forcing visibility - display:', finalDisplay, 'visibility:', finalVisibility, 'isVisible:', isVisible);
                        
                        if (!isVisible || finalDisplay === 'none' || finalVisibility === 'hidden') {
                            console.error('CRITICAL: Image is still hidden! Cannot initialize Jcrop.');
                            console.error('Image element:', $previewImg[0]);
                            console.error('Image parent:', $previewImg.parent()[0]);
                            console.error('Container:', $previewContainer[0]);
                            return;
                        }
                        
                        // Initialize Jcrop with proper dimensions
                        // Wait a bit more to ensure everything is ready
                        setTimeout(function() {
                            try {
                                // Double-check visibility before initializing
                                if (!$previewImg.is(':visible')) {
                                    console.error('Image became hidden again! Re-showing...');
                                    $previewImg.attr('style', 'display: block !important; visibility: visible !important; opacity: 1 !important; pointer-events: auto !important;');
                                    $previewContainer.show();
                                }
                                
                                // Clear any existing Jcrop instance completely
                                if (jcropApi) {
                                    try {
                                        jcropApi.destroy();
                                    } catch(e) {
                                        console.log('Error destroying Jcrop:', e);
                                    }
                                    jcropApi = null;
                                }
                                
                                // Remove all Jcrop DOM elements
                                $previewImg.siblings('.jcrop-holder').remove();
                                $previewImg.parent().find('.jcrop-holder').remove();
                                $previewImg.closest('.image-preview-container').find('.jcrop-holder').remove();
                                
                                // Verify Jcrop is available
                                if (typeof $.fn.Jcrop === 'undefined' || typeof $.fn.Jcrop !== 'function') {
                                    console.error('Jcrop not available when trying to initialize');
                                    console.error('$.fn.Jcrop type:', typeof $.fn.Jcrop);
                                    return;
                                }
                                
                                // Validate coordinates before using them
                                if (typeof initX === 'undefined' || typeof initY === 'undefined' || 
                                    typeof initWidth === 'undefined' || typeof initHeight === 'undefined' ||
                                    initWidth <= 0 || initHeight <= 0 || initX < 0 || initY < 0 ||
                                    initX + initWidth > imgWidth || initY + initHeight > imgHeight) {
                                    console.error('Invalid coordinates for Jcrop initialization:', {
                                        x: initX, y: initY, w: initWidth, h: initHeight,
                                        imgW: imgWidth, imgH: imgHeight
                                    });
                                    // Recalculate with safe defaults
                                    initWidth = Math.min(400, imgWidth - 20);
                                    initHeight = Math.floor(initWidth / cropRatio);
                                    if (initHeight > imgHeight - 20) {
                                        initHeight = imgHeight - 20;
                                        initWidth = Math.floor(initHeight * cropRatio);
                                    }
                                    initX = Math.max(0, Math.floor((imgWidth - initWidth) / 2));
                                    initY = Math.max(0, Math.floor((imgHeight - initHeight) / 2));
                                    console.log('Recalculated coordinates:', {x: initX, y: initY, w: initWidth, h: initHeight});
                                }
                                
                                // Initialize Jcrop - simplified options
                                // Jcrop setSelect format: [x1, y1, x2, y2] where (x1,y1) is top-left and (x2,y2) is bottom-right
                                // CRITICAL: Ensure x2 > x1 and y2 > y1
                                var x1 = Math.max(0, Math.floor(initX));
                                var y1 = Math.max(0, Math.floor(initY));
                                var x2 = Math.min(imgWidth, Math.floor(initX + initWidth));
                                var y2 = Math.min(imgHeight, Math.floor(initY + initHeight));
                                
                                // Final validation - ensure valid rectangle
                                if (x2 <= x1) {
                                    console.warn('x2 <= x1, adjusting...', x1, x2);
                                    x2 = Math.min(imgWidth, x1 + 100);
                                }
                                if (y2 <= y1) {
                                    console.warn('y2 <= y1, adjusting...', y1, y2);
                                    y2 = Math.min(imgHeight, y1 + Math.floor(100 / cropRatio));
                                }
                                
                                // Ensure minimum size
                                if (x2 - x1 < 100) {
                                    x2 = Math.min(imgWidth, x1 + 100);
                                    y2 = Math.min(imgHeight, y1 + Math.floor(100 / cropRatio));
                                }
                                if (y2 - y1 < Math.floor(100 / cropRatio)) {
                                    y2 = Math.min(imgHeight, y1 + Math.floor(100 / cropRatio));
                                    x2 = Math.min(imgWidth, x1 + Math.floor(100 * cropRatio));
                                }
                                
                                console.log('Final Jcrop setSelect coordinates:', [x1, y1, x2, y2]);
                                console.log('Validating: x2 > x1?', x2 > x1, 'y2 > y1?', y2 > y1);
                                
                                if (x2 <= x1 || y2 <= y1) {
                                    console.error('INVALID COORDINATES! Cannot initialize Jcrop.');
                                    console.error('x1:', x1, 'y1:', y1, 'x2:', x2, 'y2:', y2);
                                    return;
                                }
                                
                                var jcropOptions = {
                                    aspectRatio: cropRatio,
                                    setSelect: [x1, y1, x2, y2],
                                    onSelect: updateCropCoords,
                                    onChange: updateCropCoords,
                                    bgColor: 'black',
                                    bgOpacity: 0.4,
                                    minSize: [100, Math.round(100 / cropRatio)]
                                };
                                
                                // Only add trueSize if dimensions are valid and different
                                if (actualImageWidth && actualImageHeight && 
                                    actualImageWidth > 0 && actualImageHeight > 0 &&
                                    (Math.abs(imgWidth - actualImageWidth) > 1 || 
                                     Math.abs(imgHeight - actualImageHeight) > 1)) {
                                    jcropOptions.trueSize = [actualImageWidth, actualImageHeight];
                                    console.log('Using trueSize for coordinate scaling');
                                } else {
                                    console.log('Not using trueSize - dimensions match or invalid');
                                }
                                
                                console.log('Initializing Jcrop with options:', jcropOptions);
                                console.log('Image element:', $previewImg[0]);
                                console.log('Image src:', $previewImg.attr('src'));
                                console.log('Image dimensions - displayed:', imgWidth, 'x', imgHeight);
                                console.log('Image dimensions - actual:', actualImageWidth, 'x', actualImageHeight);
                                
                                // Ensure image is in the DOM and visible
                                if (!$previewImg.is(':visible')) {
                                    console.error('Image is not visible!');
                                    $previewContainer.show();
                                }
                                
                                // Try initializing Jcrop - use the simplest possible call
                                try {
                                    console.log('About to call $previewImg.Jcrop()');
                                    console.log('Image jQuery object:', $previewImg);
                                    console.log('Image element:', $previewImg[0]);
                                    console.log('Image in DOM:', $.contains(document.body, $previewImg[0]));
                                    
                                    // Initialize Jcrop
                                    $previewImg.Jcrop(jcropOptions, function() {
                                        jcropApi = this;
                                        console.log('✓ Jcrop callback executed - initialized successfully');
                                        console.log('Jcrop API:', this);
                                        
                                        // Check if selection exists
                                        try {
                                            var testCoords = this.tellSelect();
                                            console.log('Initial crop coordinates:', testCoords);
                                            if (testCoords && testCoords.w > 0 && testCoords.h > 0) {
                                                updateCropCoords(testCoords);
                                                console.log('✓ Crop coordinates set successfully');
                                                
                                                // Verify the crop box is visible and interactive
                                                setTimeout(function() {
                                                    var $holder = $previewImg.siblings('.jcrop-holder');
                                                    if ($holder.length > 0) {
                                                        console.log('✓ Jcrop holder found');
                                                        console.log('Holder CSS:', {
                                                            display: $holder.css('display'),
                                                            visibility: $holder.css('visibility'),
                                                            'pointer-events': $holder.css('pointer-events'),
                                                            'z-index': $holder.css('z-index')
                                                        });
                                                        
                                                        // Check for the selection box
                                                        var $selection = $holder.find('.jcrop-selection');
                                                        if ($selection.length > 0) {
                                                            console.log('✓ Selection box found');
                                                            console.log('Selection CSS:', {
                                                                'pointer-events': $selection.css('pointer-events'),
                                                                cursor: $selection.css('cursor')
                                                            });
                                                        } else {
                                                            console.warn('⚠ Selection box not found');
                                                        }
                                                    } else {
                                                        console.warn('⚠ Jcrop holder not found');
                                                    }
                                                }, 100);
                                            } else {
                                                console.warn('⚠ Invalid coordinates:', testCoords);
                                            }
                                        } catch(e) {
                                            console.error('Error getting coordinates:', e);
                                        }
                                    });
                                    
                                    console.log('✓ Jcrop method called successfully');
                                } catch(jcropError) {
                                    console.error('✗ Error calling Jcrop:', jcropError);
                                    console.error('Error message:', jcropError.message);
                                    console.error('Error stack:', jcropError.stack);
                                }
                            } catch(e) {
                                console.error('Error in Jcrop initialization timeout:', e);
                                console.error('Error message:', e.message);
                                console.error('Error stack:', e.stack);
                            }
                        }, 300); // Delay to ensure image is fully rendered
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
