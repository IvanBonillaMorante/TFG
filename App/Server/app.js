const express = require('express');
const app = express();
const fileupload = require('express-fileupload');
const bodyParser = require('body-parser');
const cors = require('cors');

app.use(fileupload());
app.use(cors());
app.use(express.json());

app.get("/Prueba", (req, res) => {
    res.send("Hello World");
});

app.get("/upload", (req, res) => {
    console.log(req.files.file);
    res.send(`Archivo ${req.files.file.name} subido correctamente`);
    fileupload.mv(req.files.file.path, "/home/ivan/TFG/prueba_unitaria");
});

app.listen(3000, () =>{
    console.log("Server running on port 3000");
});