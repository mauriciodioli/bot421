const btnDelete = document.querySelectorAll('.btn-delete')

if(btnDelete){
    const btnArray =   Array.from(btnDelete);
    btnArray.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            if(!confirm('Are you sure you want to delete it?')){
                e.preventDefault();
            }
        });
    });

}

const selector = document.querySelectorAll('.selctorEnvironment')

if(selector){
    console.log("selecciona")
    const btnArray =   Array.from(selector);
    btnArray.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            if(!confirm('selecciona esto')){
                e.preventDefault();
            }
        });
    });

}
