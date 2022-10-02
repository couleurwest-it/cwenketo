/*

copyright  is Tobias Bogliolo.
===============================================================
*/
//Global:
var survey = []; //Bidimensional array: [ [1,3], [2,4] ]

//Switcher function:
$(".rb-tab").click(function(){
  //Spot switcher:
    let $me = $(this);
    $me.parent().find(".rb-tab").removeClass("rb-tab-active");
    $me.addClass("rb-tab-active");
    $('[name=reponse]').val($me.attr('data-value'));
});

//Save data:
$(".trigger").click(function(){
  //Empty array:
  survey = [];
  //Push data:
  for (i=1; i<=$(".rb").length; i++) {
    var rb = "rb" + i;
    var rbValue = parseInt($("#rb-"+i).find(".rb-tab-active").attr("data-value"));
    //Bidimensional array push:
    survey.push([i, rbValue]); //Bidimensional array: [ [1,3], [2,4] ]
  };

});