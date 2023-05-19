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
            $('#tableau').DataTable({     
              "aLengthMenu": [[3, 5, 10, 25, -1], [3, 5, 10, 25, "All"]],
                "iDisplayLength": 3
               } 
            );
        } );


        $(document).ready(function() {
            $('#search_locataire_id').change(function(){
               $.post("/get_nom_locataire", {
                nom_locataire: $('#search_locataire_id').val(),
               }, function(response){ 
                   $('#show_locataire').html(response);
                   $('#show_locataire').append(response.htmlresponse);
               });
               return false;
             });
           }); 
           $(document).ready(function() {
               $('#search_appartement_id').change(function(){
                  $.post("/get_nom_appartement", {
                    nom_appartement: $('#search_appartement_id').val(),
                  }, function(response){ 
                      $('#show_appartement').html(response);
                      $('#show_appartement').append(response.htmlresponse);
                  });
                  return false;
                });
              }); 