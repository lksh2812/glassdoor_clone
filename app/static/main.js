
const generateFile = (id) =>{
   let host = window.location.host
   fetch(`http://${host}/download/review/${id}`)
   .then(response => response.json())
   // .then(result=>getDownloadModal(result['url']));
   .then(result=>getDownloadModal(result['id']))
}
const getDownloadModal = (task_id) => {
   fetch(`http://localhost:5000/get_file/${task_id}`)
   .then(res=>res.json())
   .then(result=>{
       download_url = result['url']
       let downloadButton = document.querySelector('#download-button')
       let generateButton = document.querySelector('#generate-file')
       generateButton.parentNode.removeChild(generateButton)
       downloadButton.setAttribute('href', download_url)
       downloadButton.style.display = "inline"
       downloadButton.click()

   })
}
