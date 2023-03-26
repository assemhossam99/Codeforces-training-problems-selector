document.addEventListener('DOMContentLoaded', function() {

    this.documentElement.querySelector('.hidden-list-button').addEventListener('click', () => {
        if(document.querySelector('.hidden-list').style.display == 'block'){
            document.querySelector('.hidden-list').style.display = 'none';
        }
        else {
            document.querySelector('.hidden-list').style.display = 'block';
        }
    })
    


  });
