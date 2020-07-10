/*
Author: Baixu
Date: 2020-06-23
Desc: 首页中展示某路径下目录项详细信息的数据表格fileInfo_dataGrid的相关代码
 */
//依赖脚本： global_variables.js

// toolbar变量为fileInfo_dataGrid中所用到的工具栏
const toolbar = [{
        text: '返回上级',
        iconCls: 'icon-back',
        handler: function () {
            back();
        }
    }, {
        text: '上传文件',
        iconCls: 'icon-add',
        handler: function () {
            show_upload_modal(get_data_dir());
        }
    }, {
        text: '新建文件夹',
        iconCls: 'icon-add',
        handler: function () {
            show_mkdir_modal(get_data_dir());
        }
    }, '-', {
        iconCls: 'icon-more',
        handler: function() {
            alert('显示该文件夹下的容量使用、权限说明等');
        }
    },'-',{
        text: 'Search',
        id: 'search',
        iconCls: 'icon-search',
        handler: function () {
            display_file_list(document.getElementById('path_to_go').value)
        }

}];

$(function(){
    let a = get_data_list();
    console.log(a);
    for(let i in a){
        //console.log(a[i]);
        if(a[i]['type']==='dir'){
            a[i]['icon']='<img src=\''+get_folder_icon_dir()+'\' alt="文件夹">';
        }
        else
            a[i]['icon']='<img src=\''+get_file_icon_dir()+'\' alt="文件">';
    }
    //console.log(a);
    fileInfo_dataGrid.datagrid({
        width:700,
        height:300,
        fitColumns:true,
        toolbar: toolbar,
        columns:[[
            {field:'icon'},
            {field:'type',title:'文件类型'},
            {field:'name',title:'文件名',width:200},
            {field:'size',title:'文件大小',width:200}
            ]],
        data: a,
        view: detailview,
        detailFormatter: function(rowIndex, rowData){
            return '<table class="easyui-datagrid"><tr>' +
                    '<td ><a href="#" onclick="show_remove_file_modal(get_data_dir(),\''+rowData['name']+'\',\''+rowData['type']+'\')"> 删除</a></td>' +
                    '<td><a href="#" onclick="show_rename_or_move_modal(get_data_dir(),\''+rowData['name']+'\',\''+rowData['type']+'\')">重命名/移动</a></td>'+
                    '<td><a href="#" onclick="show_download_modal(get_data_dir(),\''+rowData['name']+'\')">下载/二维码</a></td>'+
                    '</tr></table>';
            },
        onDblClickRow: function(rowIndex, rowData){
            if(rowData['type']==='dir') {
                //alert(get_data_dir());
                display_file_list(get_data_dir() + rowData['name']);
            }
            else
                preview_txt_file(get_data_dir() + rowData['name']);
            }
        });
        //.datagrid('subgrid', conf);
        //console.log('finish');
    });
