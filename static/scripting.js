function displayTime(){
            document.getElementById('time').innerHTML = new Date()
        }
        setInterval(displayTime, 1000)