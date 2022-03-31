$(document).ready(function(){

    var elbow = $('#elbow');
function setElbowAngle(angle){
  elbow.attr("transform", "rotate(" + angle + " 240 16)");
}

var shoulder = $('#shoulder');

function setShoulderAngle(angle){
  shoulder.attr("transform", "rotate(" + angle + " 16 16)");
}

var elbowSlider = $('#elbowAngle');
elbowSlider.on('input', function(event){
  var newVal = event.target.value;
  setElbowAngle(newVal);
  $('#elbowAngleOut').text(newVal);
});

var shoulderSlider = $('#shoulderAngle');
shoulderSlider.on('input', function(event){
  var newVal = event.target.value;
  setShoulderAngle(newVal);
  $('#shoulderAngleOut').text(newVal);
  });

  function randomWalk(){
    var ss=0.1
    shoulderSlider.val(Number(shoulderSlider.val()) + ((Math.random()*ss*2) - ss));
    elbowSlider.val(Number(elbowSlider.val()) + ((Math.random()*ss*2) - ss));
    var sval = shoulderSlider.val();
    setShoulderAngle(sval);
    $("#shoulderAngleOut").text(sval);
    var eval = elbowSlider.val();
    setElbowAngle(eval);
    $("#elbowAngleOut").text(eval);

  }
  setInterval(randomWalk, 20);
});
