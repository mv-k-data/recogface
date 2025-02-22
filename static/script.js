const inputId = "#js-input-file"
const errorBlockId = "#js-error"
const blockListItems = "#js-list-items"
const blockOriginalImage = "#js-original-image"
const preloderBlock = $('#js-preloader')
const allowedExtensions = ['jpg', 'jpeg', 'png']

document.querySelectorAll('.js-result-item').forEach(item => {
    item.addEventListener('click', () => {
        const href = item.getAttribute('data-href');
        if (href) {
            window.open(href, '_blank');
        }
    });
});

function isShowPreloader(el, isShow = false){
  
  if (isShow == true) {
    preloderBlock.show()
    el.hide()
  }else{
    preloderBlock.hide()
    el.show()
  }
}

$('body').on('change', inputId, function () {
  $(errorBlockId).hide()
  const this_el = $(this)
  const parentBlock = this_el.closest('div')
  
  const fileInput = this_el[0];
  const file = fileInput.files[0];

  isShowPreloader(parentBlock, true)
  if (file) {
    const fileName = file.name;
    const fileExtension = fileName.substring(fileName.lastIndexOf('.') + 1).toLowerCase();
    
    if (allowedExtensions.indexOf(fileExtension) === -1) {
        isShowPreloader(parentBlock)
        $(errorBlockId).text("Allowed files: " + allowedExtensions.join(", "))
        $(errorBlockId).show()
        this_el.val('')
        return
    }  

    const formData = new FormData();
    formData.append('file', file);

    $.ajax({
      url: '/upload', 
      type: 'POST',
      data: formData,
      processData: false, 
      contentType: false, 
      success: function(response) {
        if (response.error.length > 0) {
          $(errorBlockId).text(response.error)
          $(errorBlockId).show()  
        }else{
          $(blockListItems).html(response.content)
        }
        isShowPreloader(parentBlock)
        this_el.val('')
        $(blockOriginalImage).find('img').attr("src", response.original_image);
        $(blockOriginalImage).removeClass('js-hide')
      },
      error: function(error) {
        isShowPreloader(parentBlock)
        $(errorBlockId).text("Server Error")
        $(errorBlockId).show()
      }
    })
  }  
})