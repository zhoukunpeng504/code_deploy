/**
 * Date: 2015/6/4
 * Update: 2015/6/4
 */

function getHMS(timestamp) {
  let time = new Date(timestamp);
  let year = time.getFullYear();
  const month = (time.getMonth() + 1).toString().padStart(2, '0');
  const date = (time.getDate()).toString().padStart(2, '0');
  const hours = (time.getHours()).toString().padStart(2, '0');
  const minute = (time.getMinutes()).toString().padStart(2, '0');
  const second = (time.getSeconds()).toString().padStart(2, '0');
  return hours + ':' + minute + ':' + second;
}

function getDatetime(timestamp) {
  let time = new Date(timestamp);
  let year = time.getFullYear();
  const month = (time.getMonth() + 1).toString().padStart(2, '0');
  const date = (time.getDate()).toString().padStart(2, '0');
  const hours = (time.getHours()).toString().padStart(2, '0');
  const minute = (time.getMinutes()).toString().padStart(2, '0');
  const second = (time.getSeconds()).toString().padStart(2, '0');
  return year + month + date +' ' + hours + ':' + minute + ':' + second;
}

function show_msg(content, timeout=1200) {
  var d = dialog({
    content: content
  });
  d.show();
  setTimeout(function () {
    d.close().remove();
  }, timeout);

}
function getHMS(timestamp) {
  let time = new Date(timestamp);
  let year = time.getFullYear();
  const month = (time.getMonth() + 1).toString().padStart(2, '0');
  const date = (time.getDate()).toString().padStart(2, '0');
  const hours = (time.getHours()).toString().padStart(2, '0');
  const minute = (time.getMinutes()).toString().padStart(2, '0');
  const second = (time.getSeconds()).toString().padStart(2, '0');
  return hours + ':' + minute + ':' + second;
}

function show_ask_msgbox(title, message, ok_function, width=300, height=80){

      var detail_dialog = dialog({
        width: width,
        height: height,
        title: title,
        okValue: '确定',
        content: message,
        ok: ok_function,
        cancelValue: '取消',
        cancel: function () {
        }
      });
      detail_dialog.showModal()

}

function simple_post(url, data, ok_callback, err_callback, with_loading){
  var _dd =null
  if(with_loading){
    _dd = dialog({
        content: '加载中..',

      });
    _dd.show()
  }

  jQuery.ajax({
    method: 'POST',
    dataType: 'json',
    data: data,
    url:url,
    success: function (res){
      if(_dd)
      _dd.close().remove();
      if(ok_callback)
      ok_callback(res);
    },
    error:function (res){
      if(_dd)
      d.close().remove();
      show_msg('加载失败，请联系管理员')
      if(err_callback)
      err_callback(res);
    },
  })

}


function simple_get(url, ok_callback, err_callback,with_loading){
    var _dd =null
  if(with_loading){
  _dd = dialog({
        content: '加载中..',

      });
    _dd.show()
  }
  jQuery.ajax({
    method: 'GET',
    dataType: 'json',
    url:url,
        success: function (res){
      if(_dd)
      _dd.close().remove();
      if(ok_callback)
      ok_callback(res);
    },
    error:function (res){
      if(_dd)
      d.close().remove();
      show_msg('加载失败，请联系管理员')
      if(err_callback)
      err_callback(res);
    },
  })
}


