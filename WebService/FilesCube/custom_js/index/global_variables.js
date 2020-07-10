/*
Author: Baixu
Date: 2020-06-22
Desc: 在此文件中定义所用到的全局变量
 */

var upload_path;
function set_upload_path(dir){ upload_path = dir; }
function get_upload_path(){ return upload_path; }

const navigationTree = $('#navigationTree');
const fileInfo_dataGrid = $('#fileInfo_dataGrid');

//image_dir, _data_dir, _data_list 需要在index.html中初始化
var image_dir = {
    'file':'',
    'folder':''
};
function get_file_icon_dir(){return image_dir['file'];}
function get_folder_icon_dir(){return image_dir['folder'];}

var _data_dir;
function set_data_dir(dir){ _data_dir = dir; }
function get_data_dir() { return _data_dir; }

var _data_list;
function set_data_list(data_list){ _data_list = data_list; }
function get_data_list() { return _data_list; }

var _max_file_windows_count = 5;  //最多可以同时显示的文件预览窗口数量
var _overused_file_windows_count = 0; //超过max_file_windwos_count之后用来计数
//记录各个windows目前是否显示在页面中，true为显示，false为未显示
var file_preview_windows_status = [false, false, false, false, false] //数组长度需与_max_file_windows_count保持一致
function get_a_file_windows_id(){
    //返回一个数字，该数字被用于和某一特定字符串组合以组成一个新的id
    //组成出的这一新id不会与正在显示的file-preview-windows的id重复
    for(let i = 0; i<_max_file_windows_count; i++){
        if(file_preview_windows_status[i]===false) {
            file_preview_windows_status[i] = true;
            return i;
        }
    }
    // for循环结束仍未退出函数，说明已显示的窗口数已大于_max_file_windows_count
    _overused_file_windows_count ++;
    return _max_file_windows_count + _overused_file_windows_count - 1;
}
function recycle_a_file_windows_id(id){
    //当关闭某窗口时调用该函数，将对应的id置为 “ 未显示 ” 状态
    if(id>=0 && id<_max_file_windows_count)
        file_preview_windows_status[id] = false;
}
