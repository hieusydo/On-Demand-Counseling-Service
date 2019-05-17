var currentProblem = '';

$(document).ready(function() {
    handleAuth();
});

function handleAuth() {
    var apigClient = apigClientFactory.newClient({
        // accessKey: accessKeyId,
        // secretKey: secretAccessKey,
        // sessionToken: sessionToken
    });
    handleInputSubmit(apigClient);
}

function handleInputSubmit(apigClient) {
    $("#user-input-form").submit(function(e) {
        var message = $("#user-input").val();
        e.preventDefault();

        addUserMsgUI(message);
        sendPost(apigClient, message);

        // addBotMsgUI('hi back')

        $("#user-input").val("");
    });
}

function sendPost(apigClient, message) {
    var body = {
        "text": message,
        "sessionAttributes": {
            "currentProblem": currentProblem
        },
        "timestamp": Date.now()
    };
    var params = {};
    var additionalParams = {
        headers: {},
        queryParams: {}
    };
    apigClient.chatbotPost(params, body, additionalParams)
    .then(function(result){
        var reply = result.data.body;
        console.log(result.data)
        replyToPrint = reply['response']
        if (reply['sessionAttributes']['currentProblem'] != '') {
            currentProblem += reply['sessionAttributes']['currentProblem']
        }
        if (reply['counselorEmail'] != null && reply['counselorEmail'] != '') {
            replyToPrint += `Please click <a href="skype:${reply['counselorEmail']}?call">here</a> to get in contact.`
        }
        addBotMsgUI(replyToPrint);
    }).catch( function(err){
        console.log(err);
    });
}

function addUserMsgUI(message, username) {
    $("#chat-output").append(`
    <div class='client-chat'>
    <h3>You</h3>
    <p>${message}</p>
    </div>
    `);
}

function addBotMsgUI(message) {
    $("#chat-output").append(`
    <div class='author-chat'>
    <h3>Heka</h3>
    <p>${message}</p>
    </div>
    `);
    $("html, body").animate({ scrollTop: $(document).height() }, 1000);
}

function tokenizeUrl() {
    var vars = {};
    var parts = window.location.href.replace(/[#?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

