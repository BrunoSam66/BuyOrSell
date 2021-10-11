

function setColor(e) {    
    var target = e.target,
        count = +target.dataset.count;
   // console.log(target.dataset.count);
    //console.log(document.getElementById("marcador").className);
  if(target.dataset.count==1){
    //console.log(target.dataset.count);
    document.getElementById("marcador").className='fa fa-bookmark-o';    
  }else{ 
    //console.log(target.dataset.count);
    //console.log(target.dataset.count+ "ssssssssss");     
    document.getElementById("marcador").className='fa fa-bookmark';
  }
  target.style.color = count === 1 ? '#000000':"#FF0000"; 
  target.dataset.count = count === 1 ? 0 : 1;
  //console.log(target.dataset.count);
  //console.log(target);
  //console.log(document.getElementById("marcador").className);
}


//https://stackoverflow.com/questions/37205438/image-upload-with-preview-and-delete-option-javascript-jquery
//https://stackoverflow.com/questions/3144419/how-do-i-remove-a-file-from-the-filelist



function readURL(input,div_id) {
  //alert(div_id)
  if(div_id === undefined){
    div_id='#preview';
  }
  $(div_id).empty();
  var preview = document.querySelector(div_id);
  if (input.files){
    [].forEach.call(input.files, readAndPreview);
  }
  function readAndPreview(file) {

   // Make sure `file.name` matches our extensions criteria
    if (!/\.(jpe?g|png|gif|webp|bmp)$/i.test(file.name)) {
      alert(file.name + " is not an image");
      return false
    } // else...
    
    var reader = new FileReader();
    
    reader.addEventListener("load", function() {
      var image = new Image();
      image.height = 200;
      image.width=200;
      image.title  = file.name;
      image.src    = this.result;
      preview.appendChild(image);
    });
    
    reader.readAsDataURL(file);    
  }
}

