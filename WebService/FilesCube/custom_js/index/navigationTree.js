/*
Author: Baixu
Date: 2020-06-23
Desc: 首页左侧文件导航树的相关代码
 */
//依赖脚本： global_variables.js
$('#navigationTree').tree({
    onClick: function(node){
        //console.log('4321');
        let file_type = node.attributes['file_type'];
            switch(file_type){
                case 'dir':
                    go_to(node.attributes['file_dir']);
                    break;
                case 'file':
                    preview_txt_file(node.attributes['file_dir']);
                    break;
                case 'NoneTypeHint':
                    alert("这是一条提示信息，该文件夹下暂时没有文件");
                    break;
            }
        },
    onExpand: function(node){
        const csrf = $('input[name="csrfmiddlewaretoken"]').val();
        let file_dir = node.attributes['file_dir']
        let children_list = navigationTree.tree('getChildren', node.target);

        for(let i in children_list)
            navigationTree.tree('remove', children_list[i].target);

        $.ajax({
            url:"/get_files_under_dir/",
            type:"post",
            data:{"file_dir":file_dir,
                'csrfmiddlewaretoken': csrf,},
            success: function(data){
                data = JSON.parse(data);
                console.log(data);
                if(data['have_access'] && data['dir_exist']){
                    let file_list_to_display = data['file_list']

                    for(let i in file_list_to_display){
                        let file = file_list_to_display[i];
                        let state = 'closed';
                        if(file['file_type'] === 'file')
                            state = 'open';
                        navigationTree.tree('append', {
                            parent: node.target,
                            data: [{
                                text: file['file_name'],
                                state: state,
                                attributes:{'file_type': file['file_type'],
                                    'file_name': file['file_name'],
                                    'file_dir': file['file_dir']},
                            }],
                        });
                    }// end for

                    // 若本来为闭合状态的节点点开后没有节点加载进来，即该文件夹下没有文件，
                    // easyui会将该节点设置为文件类型，之后就不能对该节点进行展开或者折叠的操作了，
                    // 若之后该文件夹下新增了文件，用户也不能通过导航树来获取到最新状态
                    // 为了解决该问题，我们在空文件夹下加一条提示信息作为该文件夹的子节点
                    if(navigationTree.tree('isLeaf', node.target))
                        navigationTree.tree('append', {
                            parent: node.target,
                            data: {
                                text: '该文件夹下暂时没有文件哦',
                                state: 'open',
                                attributes:{'file_type': 'NoneTypeHint',
                                            'file_name': 'blank',
                                            'file_dir': 'blank',}
                            },
                        });

                }
            },//end of success: function
        });//end of ajax
    },
    onBeforeDrop: function(targetNode, sourceNode,point){
        // NoneTypeHint 代表该项是空文件夹的提示信息，不是文件或文件夹，不支持拖拽移动
        if(targetNode.attributes['file_type']==='NoneTypeHint' ||
            sourceNode.attributes['file_type']==='NoneTypeHint')
            return false;

        var target_node = navigationTree.tree('getNode',targetNode);
        if(point==='append')
            if(target_node.attributes['file_type']==='file'){
                alert("文件只能移动到文件夹中");
                return false;
            }
        if(point==='top'||point==='bottom')
            target_node = navigationTree.tree('getParent',targetNode);
        var source_node_parent = navigationTree.tree('getParent',sourceNode.target);
        if(target_node==null||source_node_parent==null){

            alert("不能移动根目录，不能将子目录移动为根目录");
            return false;
        }
        console.log(target_node.attributes);
        console.log(sourceNode.attributes);
        show_rename_or_move_modal(
            sourceNode.attributes['file_dir'],
            sourceNode.attributes['file_name'],
            sourceNode.attributes['file_type']);
        document.getElementById("rename_myModal_des_path").value = target_node.attributes['file_dir'];
        document.getElementById('rename_myModal_curr_path').value = source_node_parent.attributes['file_dir'];
        document.getElementById('rename_myModal_curr_name').value = sourceNode.attributes['file_name'];
        document.getElementById('rename_myModal_des_name').value = sourceNode.attributes['file_name'];
        return false;
        },
    onContextMenu: function(e, node){
        e.preventDefault();
        // select the node
        navigationTree.tree('select', node.target);
        // display context menu
        $('#mm').menu('show', {
            left: e.pageX,
            top: e.pageY
        });
    }
});

function refreshTreeNode(file_dir){
    $('navigationTree').tree('find',)
}
