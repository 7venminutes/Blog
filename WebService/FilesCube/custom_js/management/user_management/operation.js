/*
Author: Baixu
Date: 2020-06-24
Desc: 用户管理相关的操作代码（新建用户、删除用户的AJAX代码，获取最新数据展示在user_dg的AJAX代码）
 */

function display_user(){
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    return $.ajax({
        url: "/filescube/user_management/display_user/",
        type: "post",
        data: {"csrfmiddlewaretoken": csrf,},
        success: function (data) {
            data = JSON.parse(data);
            console.log(data);
            if (data['state'] === 'success'){
                let user_list = [];
                for (var i in data['details']){
                    let sys_admin_str = 'yes';
                    console.log(data['details']);
                    if(data['details'][i]['sys_admin']===0)
                        sys_admin_str = 'no';
                    user_list.push({'user_ID':data['details'][i]['ID'],
                        'root_dir':data['details'][i]['root_dir'],
                        'size':'-',
                        'sys_admin': sys_admin_str})
                }
                user_list = JSON.stringify(user_list);
                user_list = eval(user_list);
                console.log(user_list);
                $('#user_dg').datagrid('loadData',user_list);
            }
            else {
                alert(data['details']);
                return '12345';
            }
        }
    })
}

function make_new_user()
{
    let id = document.getElementById('new_user_id').value;
    let password = document.getElementById('new_user_password').value;
    let root_dir = $('#new_user_volume').combobox('getValue') + id + '/';
    let size = document.getElementById('new_user_size').value;
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
            url:"/filescube/user_management/make_new_user/",
            type:"post",
            data:{"id": id,
                "password": password,
                "root_dir": root_dir,
                "size": size,
                "csrfmiddlewaretoken":csrf,},
            success:function (data) {
                //改变user_dg中的展示状态
                data = JSON.parse(data);
                if(data['state']==='success'){
                    display_user();
                }
                else{
                    alert(data['details']);
                }
            }
        });
}

//与后端交互、删除用户
function remove_user_a()
{
    let user_name = document.getElementById('del_user_username').value;
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
            url:"/filescube/user_management/remove_user/",
            type:"post",
            data:{"user_name": user_name,
                "csrfmiddlewaretoken":csrf,},
            success:function (data) {
                //改变user_dg中的展示状态
                data = JSON.parse(data);
                if(data['state']==='success'){
                    display_user();
                }
                else{
                    alert(data['details']);
                }
            }
        });
}
