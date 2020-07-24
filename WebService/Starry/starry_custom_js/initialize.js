/*
初始化全局变量，判断用户登陆状态，从而决定网站的初始展示状态
 */
$.ajax({
    type : "GET",
    url : "/starry/get_user_info/",
    async: false,
    success : function(response) {
        response = JSON.parse(response);
        console.log(response)
        if(!response['user_login_state']){
            alert('先登录啊宝贝，现在没有统一登陆界面，你先用FileCube的登陆一下。再手动输入地址回来。')
            // 显示统一登陆界面
        }
        if(response['first_to_starry'])
            alert('欢迎使用Starry图像风格迁移服务，服务产生的图片将会自动保存在您的FileCube网盘中\n' +
                '存储路径： '+response['pics_store_dir'])
        file_path = response['pics_store_dir']
    }
});
