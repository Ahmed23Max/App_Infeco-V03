const btnDelete= document.querySelectorAll('.btn-delete');
        if(btnDelete) {
          const btnArray = Array.from(btnDelete);
          btnArray.forEach((btn) => {
            btn.addEventListener('click', (e) => {
              if(!confirm('Are you sure you want to delete it?')){
                e.preventDefault();
              }
            });
          })
        }
          
        $(document).ready(function() {
            $('#example').DataTable({     
              "aLengthMenu": [[3, 5, 10, 25, -1], [3, 5, 10, 25, "All"]],
                "iDisplayLength": 3
               } 
            );
        } );


