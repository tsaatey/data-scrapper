
const previewFile = (input) => {
    const file = $("input[type=file]").get(0).files[0];

    if(file){
        const reader = new FileReader();
        reader.onload = function(){
            $("#preview").attr("src", reader.result);
        }
        reader.readAsDataURL(file);
    }
}