/*
Author: Baixu
Date: 2020-07-01
Desc: 首页中展示文件上传任务信息的数据表格uploadTaskInfo_dataGrid的相关代码
 */


$('#uploadTaskInfo_dataGrid').datagrid({
    fitColumns:true,
    columns:[[
        {field:'upload_filename',title:'文件名', width: '20%', align:'center',},
        {field:'start_time',title:'任务创建时间', width: '20%', align:'center',},
        {
            field:'upload_progress',title:'上传进度[%]', width: '40%', align:'center',
            formatter: function(value, rec){
                //rec.status*100/4
                var tempval=rec.status*100/4;
                tempval = 50;
                /*
                var htmlstr = '<div class="easyui-progressbar progressbar"  value="'+tempval +'" text="'+tempval+'%">'+
                '<div class="progressbar-text" >'+tempval+'%</div>'+
                    '<div class="progressbar-value" >'+
                        '<div class="progressbar-text" >'+tempval+'%</div>'+
                    '</div>'+
                '</div>';
                 */
                var htmlstr = '<div class="easyui-progressbar progressbar"  data-options="value:'+tempval+', text:\''+tempval+'%\'  ">'+
                '<div class="progressbar-text" style="width:398px;">' + tempval + '</div><div class="progressbar-value" style="width:' + tempval + ';">&nbsp; </div>'+

                    '</div>';

                return htmlstr;
            }
        },
        {field:'state',title:'当前状态', width: '20%', align:'center',},
        ]],
    data:[{
        'upload_filename': '123',
        'start_time': '2020-07-01 14:22',
        'upload_progress': '0%',
        'state': '未启动上传',
    }],
});
