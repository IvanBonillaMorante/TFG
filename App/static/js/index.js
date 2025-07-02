const dropArea = document.querySelector(".drop-area");
const dragText = dropArea.querySelector('h2');
const button = dropArea.querySelector('button');
const input = dropArea.querySelector('#input-file');
const enviarButton = document.querySelector('#enviar');
let files;
let totalFiles;

enviarButton.addEventListener("click", (e) => {
    if(totalFiles === undefined){
        alert("Introduzca fotos para realizar la función")
    }
    else{
        let prompt = document.getElementById("prompt").value;
        let modo = document.getElementById("modo").value;
        document.querySelector("#html").innerHTML = '<img src="https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif">';
        peticion(totalFiles, prompt, modo);
    }
})

button.addEventListener("click", (e) => {
    input.click();
});

input.addEventListener("change", (e) => {
    files = input.files;
    dropArea.classList.add("active");
    showFiles(files);
    if(totalFiles === undefined){
        totalFiles = files;
    }
    else{
        totalFiles = concatFileLists(totalFiles,files);
    }
    dropArea.classList.remove('active');
});

dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add("active");
    dragText.textContent = "Suelta para subir las fotos";
});

dropArea.addEventListener("dragleave", (e) => {
    e.preventDefault();
    dropArea.classList.remove("active");
    dragText.textContent = "Arrastra todas las imagenes que quieras procesar";
});

dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    files = e.dataTransfer.files;
    showFiles(files);
    if(totalFiles === undefined){
        totalFiles = files;
    }
    else{
        totalFiles = concatFileLists(totalFiles,files);
    }
    dropArea.classList.remove("active");
    dragText.textContent = "Arrastra todas las imagenes que quieras procesar";
});

function showFiles(files){
    if (files.length === undefined){
        processFile(files);
    }
    else{
        for(const file of files){
            processFile(file);
        }
    }
}

function processFile(file){
    const docType = file.type;
    const validExtensions = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/jfif'];

    if(validExtensions.includes(docType)){
        //archivo valido
        const fileReader = new FileReader();
        const id = `file-${Math.random().toString(32).substring(7)}`;

        fileReader.addEventListener('load', e => {
            const fileUrl = fileReader.result;
            const image = `
                <div id= "${id}" class="">
                    <img src="${fileUrl}" alt="${file.name}" width="50">
                    <div class="status">
                        <span>${file.name}</span>
                        <span class="status-text">
                            Loading...
                        </span>
                    </div>
                </div>
            `;
            const html = document.querySelector("#preview").innerHTML;
            document.querySelector("#preview").innerHTML = image + html;
        })
        fileReader.readAsDataURL(file);
        peticionAjax();
    }
    else {
        //archivo no valido
        alert("No es un archivo valido");
    }
}

function peticionAjax(){
    let obj = new XMLHttpRequest();
    let url = 'inicio.html';

    obj.onreadystatechange = function(){
        if (this.readyState == 4 && this.status == 200){
            console.log(this.responseText);
        }
        else if(this.status == 404){
            console.log("Error archivo no encontrado");
        }
    }
    obj.open("POST", url);
    obj.send();

}

async function peticion(images, prompt, modo) {
    const myData = new FormData();

    myData.append("prompt", prompt);
    myData.append("modo", modo);
    for(const image of images) {
        myData.append("lista", image, image.name);
    }

    await fetch("http://127.0.0.1:6008/imagenes", {
        method: 'POST',
        body: myData
    })
        .then(response => response.blob())
        .then(finalData => {
            console.log("Files has been uploaded successfully");
        })
        .catch(err=>{
            console.log("Error found:", err);
        })
    window.location.href = "descarga"
}

function concatFileLists(fileList1, fileList2) {
  const concatenatedList = new DataTransfer(); // Crear un nuevo objeto DataTransfer

  // Agregar los elementos del primer FileList al nuevo DataTransfer
  for (let i = 0; i < fileList1.length; i++) {
    concatenatedList.items.add(fileList1[i]);
  }

  // Agregar los elementos del segundo FileList al nuevo DataTransfer
  for (let i = 0; i < fileList2.length; i++) {
    concatenatedList.items.add(fileList2[i]);
  }

  // Devolver un nuevo FileList a partir del nuevo DataTransfer
  return concatenatedList.files;
}
