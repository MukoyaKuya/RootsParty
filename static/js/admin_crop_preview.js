/**
 * Admin Crop Preview Enhancement
 * Ensures django-image-cropping widgets are visible and properly initialized
 */
(function($) {
    'use strict';
    
    function ensureCroppingVisible() {
        // Find all cropping input fields
        $('input[type="hidden"][id*="cropping"]').each(function() {
            var $croppingField = $(this);
            var $row = $croppingField.closest('.form-row, .field-box, .form-group, .unfold-fieldset, .field');
            
            // Ensure the row is visible
            if ($row.length) {
                $row.show().css('display', 'block');
                
                // Also show parent fieldset if collapsed
                var $fieldset = $row.closest('fieldset');
                if ($fieldset.length && $fieldset.hasClass('collapsed')) {
                    $fieldset.removeClass('collapsed');
                }
            }
            
            // Find and show the cropping widget
            var $widget = $croppingField.siblings('.image-ratio').first();
            if ($widget.length === 0) {
                // Try to find it in parent containers
                $widget = $croppingField.closest('.form-row, .field-box, .form-group, .unfold-fieldset, .field').find('.image-ratio').first();
            }
            
            if ($widget.length > 0) {
                $widget.show().css({
                    'display': 'block',
                    'visibility': 'visible',
                    'opacity': '1'
                });
            }
        });
        
        // Also ensure all .image-ratio widgets are visible
        $('.image-ratio').each(function() {
            var $widget = $(this);
            if ($widget.is(':hidden') || $widget.css('display') === 'none' || $widget.css('visibility') === 'hidden') {
                $widget.show().css({
                    'display': 'block',
                    'visibility': 'visible',
                    'opacity': '1'
                });
            }
        });
    }
    
    function initializeCropping() {
        // Wait for django-image-cropping to load
        if (typeof $.fn.Jcrop === 'undefined') {
            // Jcrop not loaded yet, wait a bit more
            setTimeout(initializeCropping, 200);
            return;
        }
        
        // Ensure widgets are visible
        ensureCroppingVisible();
        
        // Check if there are any images that need cropping initialization
        $('.image-ratio img').each(function() {
            var $img = $(this);
            var $container = $img.closest('.image-ratio');
            
            // If Jcrop hasn't been initialized on this image yet
            if ($container.find('.jcrop-holder').length === 0 && $img.attr('src')) {
                // The widget should initialize automatically, but ensure it's visible
                $container.show();
            }
        });
    }
    
    $(document).ready(function() {
        // Initial check after page load
        setTimeout(function() {
            ensureCroppingVisible();
            initializeCropping();
        }, 500);
        
        // Check again after a longer delay (for async loading)
        setTimeout(function() {
            ensureCroppingVisible();
            initializeCropping();
        }, 1500);
        
        // Check one more time after even longer delay
        setTimeout(function() {
            ensureCroppingVisible();
            initializeCropping();
        }, 3000);
        
        // Monitor for new image uploads
        $(document).on('change', 'input[type="file"]', function() {
            var $fileInput = $(this);
            var fieldId = $fileInput.attr('id');
            
            // Wait for image to be processed
            setTimeout(function() {
                ensureCroppingVisible();
                initializeCropping();
            }, 1000);
        });
        
        // Monitor for dynamically added content (e.g., inlines)
        if (typeof django !== 'undefined' && django.jQuery) {
            django.jQuery(document).on('formset:added', function() {
                setTimeout(function() {
                    ensureCroppingVisible();
                    initializeCropping();
                }, 500);
            });
        }
    });
    
    // Also run when DOM is updated (for AJAX forms)
    if (typeof MutationObserver !== 'undefined') {
        var observer = new MutationObserver(function(mutations) {
            var shouldCheck = false;
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length > 0) {
                    // Check if any added node is related to cropping
                    $(mutation.addedNodes).each(function() {
                        if ($(this).find('.image-ratio, input[id*="cropping"]').length > 0) {
                            shouldCheck = true;
                        }
                    });
                }
            });
            if (shouldCheck) {
                setTimeout(function() {
                    ensureCroppingVisible();
                    initializeCropping();
                }, 300);
            }
        });
        
        $(document).ready(function() {
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    }
})(django.jQuery || jQuery);
