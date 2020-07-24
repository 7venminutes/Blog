/*
Author: Baixu
Date: 2020-07-23
Desc: starry前端全局变量
 */

let file_path = '';
let user_login = false;

function pause_sleep(d){
    for(let t = Date.now();Date.now() - t <= d;);
}
