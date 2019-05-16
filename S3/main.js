var botreply="botreply";

function displayResponse(botreply) {
    console.log(botreply)
    $('#chat-output').append(`
                             <div class='user-message'>
                             <div class='message'>
                             ${botreply}
                             </div>
                             </div>`);
    
}

$(document).keypress(function (e) {
                     if (e.which==13) {
                     var message = $("#user-input").val();
                     console.log(message);
                     $('#chat-output').append(`
                                              <div class='bot-message'>
                                              <div class='message'>
                                              ${message}
                                              </div>
                                              </div>`);

 
    displayResponse(botreply);     
                     }
                     }
   
  $("#user-input").val("");

  return false;
  
  }
});
console.log('work');

