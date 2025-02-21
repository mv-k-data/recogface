document.querySelectorAll('.js-result-item').forEach(item => {
    item.addEventListener('click', () => {
        const href = item.getAttribute('data-href');
        if (href) {
            window.open(href, '_blank');
        }
    });
});

const input_id = "#js-input-file"
const error_block_id = "#js-error"
const allowedExtensions = ['jpg', 'jpeg', 'png']

function isShowPreloader(el, isShow = false){
  const preloder_block = $('#js-preloader')
  if (isShow == true) {
    preloder_block.show()
    el.hide()
  }else{
    preloder_block.hide()
    el.show()
  }
}

$('body').on('change', input_id, function () {
  $(error_block_id).hide()
  const parent_block = $(this).closest('div')
  
  const fileInput = $(this)[0];
  const file = fileInput.files[0];

  isShowPreloader(parent_block, true)
  if (file) {
    const fileName = file.name;
    const fileExtension = fileName.substring(fileName.lastIndexOf('.') + 1).toLowerCase();
    
    if (allowedExtensions.indexOf(fileExtension) === -1) {
        isShowPreloader(parent_block, false)
        $(error_block_id).text("Allowed files: " + allowedExtensions.join(", "))
        $(error_block_id).show()
        $(this).val('')
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
        console.log('OK', response);
        ///тут обробляти результати
        isShowPreloader(parent_block, false)
      },
      error: function(error) {
        // isShowPreloader(parent_block, false)
        // $(error_block_id).text("Server Error")
        // $(error_block_id).show()
      }
    })
  }  
})