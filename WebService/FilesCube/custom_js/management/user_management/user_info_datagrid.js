/*
Author: Baixu
Date: 2020-06-24
Desc: 定义管理界面中用户信息数据表格user_dg的相关行为
 */

$('#user_dg').datagrid({
    width:700,
    height:300,
    fitColumns:true,
    toolbar:$('#tb'),
    columns:[[
        {field:'user_ID',title:'用户名',width:200},
        {field:'root_dir',title:'用户根目录',width:200},
        {field:'size',title:'容量配额',width:200},
        {field:'sys_admin',title:'是否为系统管理员',width:200}
        ]],
    view: detailview,
    detailFormatter: function(rowIndex, rowData){
        var root_dir_dbl_slash = rowData['root_dir'].replace(/\\/g,'\\\\');
        return '<table class="easyui-datagrid"><tr>' +
            '<td ><a href="#" onclick="show_del_user_modal(\'' + rowData['user_ID'] + '\')"> 删除</a></td>' +
            '<td ><a href="#" onclick="show_modify_user_modal(\''+rowData['user_ID']+'\',\''+root_dir_dbl_slash+'\')"> 修改主目录</a></td>' +
            '</tr></table>';
    }
});
