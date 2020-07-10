/*
Author: Baixu
Date: 2020-06-24
Desc: 定义管理界面中用户信息数据表格user_dg的相关行为
 */

$('#volume_dg').datagrid({
    width:700,
    height:300,
    fitColumns:true,
    columns:[[
        {field:'volume_path',title:'卷在系统中的路径',width:200},
        {field:'actual_path',title:'卷的实际路径',width:200},
        {field:'size',title:'卷容量',width:200},
        {field:'volume_type',title:'卷的种类',width:200}
        ]],
    view: detailview,
    detailFormatter: function(rowIndex, rowData){
        var root_dir_dbl_slash = rowData['actual_path'].replace(/\\/g,'\\\\');
        var data = '{\'path_in_hfs\': \''+rowData['volume_path']+'\', \'actual_path\': \''+root_dir_dbl_slash+'\'}';
        return '<table class="easyui-datagrid"><tr>' +
            '<td ><a href="#" onclick="show_del_volume_modal(\''+rowData['volume_path']+'\', \''+root_dir_dbl_slash+'\')"> 删除</a></td>' +
            '</tr></table>';
    }
});
