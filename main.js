// 目标日期对应的剩余秒数
let date_left = {}

// 发起post请求，请求成功或失败都会执行回调
function doPost(url, data, callback) {
    try {
        let xhr = new XMLHttpRequest()
        xhr.timeout = 1800000

        let handleEvent = (ev) => {
            if (xhr.readyState != XMLHttpRequest.DONE) {
                return
            }

            if ((xhr.readyState == XMLHttpRequest.DONE) && (xhr.status == 200)) {
                let rsp = JSON.parse(xhr.responseText)
                callback(rsp)
            }
            else {
                console.log("请求失败:", xhr.status, ", rsp:", xhr.responseText)
                callback({})
            }
        }
        xhr.addEventListener("readystatechange", handleEvent)

        xhr.open("POST", url)
        xhr.setRequestHeader("Content-type", "application/json")
        xhr.send(JSON.stringify(data))
    } catch (err) {
        console.log("网络请求异常:", err)
        callback({})
    } finally {
    }
}

function addMainRegion() {
    let div_main = document.createElement("div");
    div_main.id = "main";
    div_main.classList.add("main");

    let div_app = document.querySelector("#app");
    div_app.appendChild(div_main);
}

function displayText(date_id, text) {
    let out = document.querySelector("#" + date_id + "_text");
    if (out != null) {
        out.innerHTML = text;
    }
}

function genColor(index, total) {
    // HSL 颜色模式，保持饱和度和亮度固定，通过色相来区分不同颜色
    const hue = (index * 360 / total) % 360; // 色相均匀分布
    return `hsl(${hue}, 70%, 50%)`; // 饱和度70%，亮度50%
}

function addDateCtrl(index, total, date_id, date_value, desc, ) {
    let input_date = document.createElement("input");
    input_date.type = "date";
    input_date.id = date_id;
    input_date.classList.add("input_date");
    input_date.value = date_value;
    input_date.readOnly = true;
    // input_date.disabled = true;
    // input_date.onchange = () => {
    //     displayText(date_id, "");
    //     worker();
    // };

    let input_label = document.createElement("label");
    input_label.innerHTML = desc;
    input_label.htmlFor = date_id;
    input_label.classList.add("label");
    input_label.classList.add("label_" + date_id);
    input_label.style.color = genColor(index, total)

    let output_text = document.createElement("div");
    output_text.id = date_id + "_text";
    output_text.innerHTML = "加载中...";
    output_text.classList.add("date_text");

    let div_input = document.createElement("div");
    div_input.id = "div_" + date_id;
    div_input.classList.add("date_wrap");
    div_input.appendChild(input_label);
    div_input.appendChild(input_date);
    div_input.appendChild(output_text);

    let div_app = document.querySelector("#main");
    div_app.appendChild(div_input);
}

function worker() {
    let all_date_ctrl = document.querySelectorAll(".input_date");
    for (let i = 0; i < all_date_ctrl.length; ++i) {
        let date_obj = all_date_ctrl[i];
        if (date_obj.value == "") {
            continue;
        }

        // let ann_time = new Date(date_obj.value + " 00:00:00").getTime() / 1000;
        // let now_time = new Date().getTime() / 1000;
        // console.log("worker|", date_obj.id, "|", ann_time, "|", now_time);

        // out_text = "";
        // if (now_time >= ann_time) {
        //     let next_year = parseInt(date_obj.value.slice(0, 4)) + 1;
        //     let new_time_str = next_year + date_obj.value.slice(4);
        //     ann_time = new Date(new_time_str + " 00:00:00").getTime() / 1000;
        // } else {
        // }

        // let left_time = ann_time - now_time;
        if (date_obj.id in date_left) {
            let left_time = date_left[date_obj.id] || 0
            if (left_time <= 0) {
                displayText(date_obj.id, "请刷新页面");
            } else {
                let left_days = parseInt(left_time / 86400);
                let left_hour = parseInt((left_time - left_days * 86400) / 3600);
                let left_min = parseInt(
                    (left_time - left_days * 86400 - left_hour * 3600) / 60
                );
                let left_sec = parseInt(
                    left_time - left_days * 86400 - left_hour * 3600 - left_min * 60
                );
                // console.log("ann time:", ann_time, "|left time:", left_time);

                displayText(
                    date_obj.id, "还剩 " + left_days + " 天" + left_hour + " 小时" + left_min + " 分钟" + left_sec + " 秒"
                );

                if (left_time > 0) {
                    date_left[date_obj.id]--
                }
            }
        }
    }
    setTimeout(worker, 1000);
}

function main() {
    addMainRegion()

    doPost('/config', {}, (rsp) => {
        console.log("config:", rsp)
        console.log("config:", JSON.stringify(rsp))
        if (rsp.length == 0) {
            return;
        }

        let total = rsp.length
        for (let i = 0; i < total; ++i) {
            let item = rsp[i];
            if (item.length < 4) {
                continue
            }

            date_id = "date" + (i + 1)
            addDateCtrl(i, total, date_id, item[2], item[0] + (item[1] ? "(农历)" : ""));
            date_left[date_id] = item[3]
        }

        // addDateCtrl(0, 4, "date1", "认识日");
        // addDateCtrl(1, 4, "date2", "结婚日");
        // addDateCtrl(2, 4, "date3", "领证日");
        // addDateCtrl(3, 4, "date4", "生日");

        worker();
    })
}

window.onload = () => {
    main();
}
