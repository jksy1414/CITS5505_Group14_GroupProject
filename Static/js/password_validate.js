document.addEventListener('DOMContentLoaded', function(){
    let password = document.getElementById('new_password');
    let confirmPassword = document.getElementById('confirm_password');
    let errorDiv = document.getElementById('error-message')
    let strengthDiv = document.getElementById('strength-indicator');
    let submitBtn = document.getElementById('submitBtn');

    function validatePassword(){
        //if documents not exist to avoid bugs.
        if(!password || !errorDiv || !submitBtn) {
            return; 
        }

        let pwd = password.value;
        //check if confirmPassword dom exist
        let confirmPwd = confirmPassword? confirmPassword.value : null;
        let errorMsg = "";

        //pwd level scores
        let strengthScore = 0;

        if (pwd.length >=8 ) strengthScore++;
        if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strengthScore++;
        if(/\d/.test(pwd)) strengthScore++;
        if(/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) strengthScore++;

        //show strengthScore colors
        if(strengthDiv){
            if(pwd.length>0){
                if(strengthScore<=1){
                    strengthDiv.textContent = "Weak";
                    strengthDiv.style.color = "red";
                }else if (strengthScore === 2 || strengthScore === 3){
                    strengthDiv.textContent = "Medium";
                    strengthDiv.style.color = "orange";
                }else if (strengthScore === 4){
                    strengthDiv.textContent = "Strong";
                    strengthDiv.style.color = "green";
                }
            // if password input has content, clear
            }else{
                strengthDiv.textContent ="";
            }
        }
        
        //show err msg if it exists.
        if (pwd.length<8) {
            errorMsg = "Password must be at least 8 characters.";
        }else if (!/[a-z]/.test(pwd) || !/[A-Z]/.test(pwd) || !/\d/.test(pwd) || !/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) {
            errorMsg = "Password must contain lowercase, uppercase, number, and special character.";
        }else if (confirmPwd !== null && pwd !== confirmPwd) {
            errorMsg = "Passwords do not match.";
        }
        //display err div if msg exists.
        if(errorMsg !== ""){
            errorDiv.textContent = errorMsg;
            errorDiv.style.display = "block";
            password.style.border = "2px solid red";
            if (confirmPassword) confirmPassword.style.border = "2px solid red";
            submitBtn.disabled = true;
        } else {
            errorDiv.style.display = "none";
            password.style.border = "";
            if (confirmPassword) confirmPassword.style.border = "";
            submitBtn.disabled = false;
        }
    }
    
    if(password) password.addEventListener('input', validatePassword);
    if(confirmPassword) confirmPassword.addEventListener('input', validatePassword);
});
