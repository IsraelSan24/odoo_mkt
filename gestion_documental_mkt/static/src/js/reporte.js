
$(document).ready(function(){

	var numerorequerimiento = 0;
  var numeroliquidacion = 0;
  var numerogastos = 0;
  var numeroequipos = 0;
  
  $('.decimales').on('input', function () {
    this.value = this.value.replace(/[^0-9,.]/g, '').replace(/,/g, '.');
  });

  $("#enviar_liquidacion").click(function(){
		  let fecha_solicitud = new Date().toLocaleDateString();
      let hora_solicitud = new Date().toLocaleTimeString();
      $("#idnumeric_liquidacion").val(numeroliquidacion++);
      $("#fecha_liquidacion").val(fecha_solicitud + " "+hora_solicitud);

      var valor = $("#valor").val()==""? 0:$("#valor").val();
      var total = $("#total_liquidacion").val();
      var resultado = parseFloat(total) - parseFloat(valor)
      let resultado_final = parseFloat(resultado).toFixed(2)
      $("#saldo_liquidacion").val(resultado_final);

  });

	$("#enviar_requerimiento").click(function(){
    let fecha_solicitud = new Date().toLocaleDateString();
    let hora_solicitud = new Date().toLocaleTimeString();
    $("#idnumeric_requerimiento").val(numerorequerimiento++);
    $("#fecha_solicitud").val(fecha_solicitud + " "+hora_solicitud);
  });

  $("#enviar_equipos").click(function(){
    let fecha_solicitud = new Date().toLocaleDateString();
    let hora_solicitud = new Date().toLocaleTimeString();
    $("#idnumeric_equipos").val(numeroequipos++);
    $("#fecha_equipos").val(fecha_solicitud + " "+hora_solicitud);
  });

  $("#enviar_gastos").click(function(){
      let fecha_solicitud = new Date().toLocaleDateString();
      let hora_solicitud = new Date().toLocaleTimeString();
      $("#idnumeric_gastos").val(numerogastos++);
      $("#emision").val(fecha_solicitud + " "+hora_solicitud);

      var fecha_tabla1 =  $("#fecha_tabla1").val()==""?"":$("#fecha_tabla1").val();
      var fecha_tabla2 =  $("#fecha_tabla2").val()==""?"":$("#fecha_tabla2").val();
      var fecha_tabla3 =  $("#fecha_tabla3").val()==""?"":$("#fecha_tabla3").val();
      var fecha_tabla4 =  $("#fecha_tabla4").val()==""?"":$("#fecha_tabla4").val();
      var fecha_tabla5 =  $("#fecha_tabla5").val()==""?"":$("#fecha_tabla5").val();
      var fecha_tabla6 =  $("#fecha_tabla6").val()==""?"":$("#fecha_tabla6").val();
      var fecha_tabla7 =  $("#fecha_tabla7").val()==""?"":$("#fecha_tabla7").val();
      var fecha_tabla8 =  $("#fecha_tabla8").val()==""?"":$("#fecha_tabla8").val();
      var fecha_tabla9 =  $("#fecha_tabla9").val()==""?"":$("#fecha_tabla9").val();
      var fecha_tabla10 =  $("#fecha_tabla10").val()==""?"":$("#fecha_tabla10").val();

      var fecha_general = [fecha_tabla1,fecha_tabla2,fecha_tabla3,fecha_tabla4,fecha_tabla5,fecha_tabla6,fecha_tabla7,fecha_tabla8,fecha_tabla9,fecha_tabla10];


      var monto1= $("#importe1").val()==""? 0:$("#importe1").val();
      var monto2= $("#importe2").val()==""? 0:$("#importe2").val();
      var monto3= $("#importe3").val()==""? 0:$("#importe3").val();
      var monto4= $("#importe4").val()==""? 0:$("#importe4").val();
      var monto5= $("#importe5").val()==""? 0:$("#importe5").val();
      var monto6= $("#importe6").val()==""? 0:$("#importe6").val();
      var monto7= $("#importe7").val()==""? 0:$("#importe7").val();
      var monto8= $("#importe8").val()==""? 0:$("#importe8").val();
      var monto9= $("#importe9").val()==""? 0:$("#importe9").val();
      var monto10= $("#importe10").val()==""? 0:$("#importe10").val();

      var monto_general = [monto1,monto2,monto3,monto4,monto5,monto6,monto7,monto8,monto9,monto10];

      
      var resultadofinal1=0;
      var resultadofinal2=0;
      var resultadofinal3=0;
      var resultadofinal4=0;
      var resultadofinal5=0;

      var fechas1="";
      var fechas2="";
      var fechas3="";
      var fechas4="";
      var fechas5="";

      
      var contador1=0;
      var contador2=20;
      var contador3=20;
      var contador4=20;
      //var contador5=0;

      var resultado1 = 0;
      var resultado2 = 0;
      var resultado3 = 0;
      var resultado4 = 0;
      var resultado5 = 0;


      for (let i = 0; i < fecha_general.length; i++){
        if (fecha_general[i] == fecha_general[0]){
            fechas1 = fecha_general[0];
            resultado1 += parseFloat(monto_general[i]);
            resultadofinal1 = resultado1;
            contador1 = i + 1;
        }
      }
      for (let o = contador1; o < fecha_general.length; o++){
        if (fecha_general[contador1] !=""){
          if (fecha_general[o] == fecha_general[contador1]){
              fechas2 = fecha_general[contador1];
              resultado2 += parseFloat(monto_general[o]);
              resultadofinal2 = resultado2;
              contador2 = o + 1;
            
          }
        }
      }
      for (let a = contador2; a < fecha_general.length; a++){
        if (fecha_general[contador2] !=""){
          if (fecha_general[a] == fecha_general[contador2]){
              fechas3 = fecha_general[contador2];
              resultado3 += parseFloat(monto_general[a]);
              resultadofinal3 = resultado3;
              contador3 = a + 1;
            
          }
        }
      }
      for (let s = contador3; s < fecha_general.length; s++){
        if (fecha_general[contador3] !=""){
          if (fecha_general[s] == fecha_general[contador3]){
              fechas4 = fecha_general[contador3];
              resultado4 += parseFloat(monto_general[s]);
              resultadofinal4 = resultado4;
              contador4 = s + 1;
            
          }
        }
      }

      for (let w = contador4; w < fecha_general.length; w++){
        if (fecha_general[contador4] !=""){
          if (fecha_general[w] == fecha_general[contador4]){
              fechas5 = fecha_general[contador4];
              resultado5 += parseFloat(monto_general[w]);
              resultadofinal5 = resultado5;
            
          }
        }
      }
  
        
      $("#fecha_importe1").val(fechas1);
      $("#importe_total_fecha1").val(resultadofinal1);

      if(resultadofinal2 != 0 ){
        $("#fecha_importe2").val(fechas2);
        $("#importe_total_fecha2").val(resultadofinal2);
      }

      if(resultadofinal3 != 0 ){
        $("#fecha_importe3").val(fechas3);
        $("#importe_total_fecha3").val(resultadofinal3);
      }

      if(resultadofinal4 != 0 ){
        $("#fecha_importe4").val(fechas4);
        $("#importe_total_fecha4").val(resultadofinal4);
      }
      if(resultadofinal5 != 0 ){
        $("#fecha_importe5").val(fechas5);
        $("#importe_total_fecha5").val(resultadofinal5);
      }
    


  });

  $('#form_liquidaciones').on('change', function() {

    var monto1= $("#monto1").val()==""? 0:$("#monto1").val();
    var monto2= $("#monto2").val()==""? 0:$("#monto2").val();
    var monto3= $("#monto3").val()==""? 0:$("#monto3").val();
    var monto4= $("#monto4").val()==""? 0:$("#monto4").val();
    var monto5= $("#monto5").val()==""? 0:$("#monto5").val();
    var monto6= $("#monto6").val()==""? 0:$("#monto6").val();
    var monto7= $("#monto7").val()==""? 0:$("#monto7").val();
    var monto8= $("#monto8").val()==""? 0:$("#monto8").val();
    var monto9= $("#monto9").val()==""? 0:$("#monto9").val();
    var monto10= $("#monto10").val()==""? 0:$("#monto10").val();
    var monto11= $("#monto11").val()==""? 0:$("#monto11").val();
    var monto12= $("#monto12").val()==""? 0:$("#monto12").val();
 
   
    var resultado = parseFloat(monto1) + parseFloat(monto2) + parseFloat(monto3) + parseFloat(monto4) + parseFloat(monto5) + parseFloat(monto6) + parseFloat(monto7) + parseFloat(monto8) +
    parseFloat(monto9) + parseFloat(monto10) + parseFloat(monto11) + parseFloat(monto12);
    
    let resultado_final = parseFloat(resultado).toFixed(2)
    $("#total_liquidacion_mostrar").html(resultado_final);
    $("#total_liquidacion").val(resultado_final);

  });

  $('#form_gastos').on('change', function() {

    var monto1= $("#importe1").val()==""? 0:$("#importe1").val();
    var monto2= $("#importe2").val()==""? 0:$("#importe2").val();
    var monto3= $("#importe3").val()==""? 0:$("#importe3").val();
    var monto4= $("#importe4").val()==""? 0:$("#importe4").val();
    var monto5= $("#importe5").val()==""? 0:$("#importe5").val();
    var monto6= $("#importe6").val()==""? 0:$("#importe6").val();
    var monto7= $("#importe7").val()==""? 0:$("#importe7").val();
    var monto8= $("#importe8").val()==""? 0:$("#importe8").val();
    var monto9= $("#importe9").val()==""? 0:$("#importe9").val();
    var monto10= $("#importe10").val()==""? 0:$("#importe10").val();
 
   
    var resultado = parseFloat(monto1) + parseFloat(monto2) + parseFloat(monto3) + parseFloat(monto4) + parseFloat(monto5) + parseFloat(monto6) + parseFloat(monto7) + parseFloat(monto8) + parseFloat(monto9) + parseFloat(monto10); 
    let resultado_final = parseFloat(resultado).toFixed(2)
    $("#total_gastos_mostrar").html(resultado_final);
    $("#total_gastos").val(resultado_final);

  });
  
});