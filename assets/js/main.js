jQuery(document).ready(function($) {

    /* Skill bar animation */
    $('.level-bar-inner').css('width', '0');

    $(window).on('load', function() {
        $('.level-bar-inner').each(function() {
            var itemWidth = $(this).data('level');
            $(this).animate({ width: itemWidth }, 900);
        });
    });

});

/* Language toggle */
function setLanguage(lang) {
    if (lang === 'en') {
        jQuery(".english").removeClass("hidden");
        jQuery(".spanish").addClass("hidden");
        jQuery("#btn-en").addClass("active");
        jQuery("#btn-es").removeClass("active");
    } else {
        jQuery(".spanish").removeClass("hidden");
        jQuery(".english").addClass("hidden");
        jQuery("#btn-es").addClass("active");
        jQuery("#btn-en").removeClass("active");
    }
}
