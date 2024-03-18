document.addEventListener('DOMContentLoaded', function () {
  var options = {
    zone: document.getElementById('joystick'),
    mode: 'static',
    position: { left: '50%', top: '50%' },
    size: 150,
    color: 'blue',
  };

  var manager = nipplejs.create(options);

  // Add event listeners for the new buttons
  document.getElementById('forward').addEventListener('click', function () {
    socket.emit('message', 'Move forward');
  });

  document.getElementById('backward').addEventListener('click', function () {
    socket.emit('message', 'Move backward');
  });

  document.getElementById('left').addEventListener('click', function () {
    socket.emit('message', 'Turn left');
  });

  document.getElementById('right').addEventListener('click', function () {
    socket.emit('message', 'Turn right');
  });
  manager.on('move', function (evt, data) {
    // Send joystick data (direction and force) to server via socket.io
    socket.emit('joystick', { direction: data.direction.angle, force: data.force });
  });

  var recognition = new webkitSpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;

  document.getElementById('start').addEventListener('click', function () {
    recognition.start();
    // Inform server about voice control start
    socket.emit('message', 'Voice control started');
  });

  document.getElementById('stop').addEventListener('click', function () {
    recognition.stop();
    // Inform server about voice control stop
    socket.emit('message', 'Voice control stopped');
  });

  recognition.onresult = function (event) {
    var transcript = event.results[event.results.length - 1][0].transcript;
    // Send voice command transcript to server via socket.io
    socket.emit('voice', transcript);
  };

  document.getElementById('break').addEventListener('click', function () {
    // Send break command to server via socket.io
    socket.emit('message', 'Emergency break');
  });

  var socket = io.connect('http://' + document.domain + ':' + location.port);
});
