/**
 * Created by tdong on 22.08.16.
 */



$(document).ready(function() {
    draw("ch_canvas");
    draw("de_canvas");
    draw("en_canvas");

    $(".dropdown-menu li a").click(function(){

       // $(".btn:first-child").text($(this).text());
       // $(".btn:first-child").val($(this).text());

    });

})
 
function draw(where) {
    var canvas = document.getElementById(where);

    if (canvas.getContext) {
        var ctx = canvas.getContext("2d");

        ctx.fillStyle = "rgb(200,0,0)";
        ctx.fillRect(10, 10, 55, 50);

        ctx.fillStyle = "rgba(0,0,200,0.5)";
        ctx.fillRect(30, 30, 55, 50);
    } else {
        alert("Canvas isn't supported.");
    }
}