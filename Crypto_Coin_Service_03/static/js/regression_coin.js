console.log("❄❄❄❄❄❄❄❄");
let anal_btn;
let ele_coin_name;
let timegap;
let res_contain;
let closeBtn;
async function get_coinname() {
  ele_coin_name = window.document.getElementById("coinname");
  timegap = document.getElementById("timegap");
  res_contain = document.getElementById("res_contain");
  closeBtn = document.getElementById("closeBtn");
  const conn = await fetch("/coin_name");
  const coinnames = await conn.json();
  let inHtml = "";
  for (let i = 0; i < coinnames.eng_name.length; i++) {
    inHtml += `<option value="${coinnames.eng_name[i]}"> ${coinnames.han_name[i]}(${coinnames.eng_name[i]})></option>`;
  }
  ele_coin_name.innerHTML = inHtml;
  anal_btn = document.getElementById("anal_btn");

  add_Event();
}
function add_Event() {
  closeBtn.addEventListener("click", () => {
    res_contain.style.display = "none";
  });
  anal_btn.addEventListener("click", async function () {
    console.log("verification✔");
    const coinname = ele_coin_name.value;
    const timegaps = timegap.value;
    const padding = await fetch("/user_data", {
      method: "post",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ coinname, timegaps }),
    }).catch((err) => {
      console.log(err);
    });
    let inHtml = "";
    if (padding) {
      const info_data = await padding.json();
      console.log(info_data);
      let today_date = new Date();
      today_date.setDate(today_date.getDate() + 1);
      let today_str = today_date.toLocaleString("ko-kr");
      let ghtml = `<h2 style="display:inline;padding:1rem;color:rgb(32, 59, 133); font-size: 1.3rem;">
      ${coinname} expected price </h2>
      <p style="font-size:1.2rem; margin-bottom:1rem;color:darkgrey">high error rate(${parseInt(
        (info_data["err_rate"]["high"] * 100 * 100) / 100
      )}%)&nbsp&nbsp&nbsp
      current error rate(${parseInt(
        (info_data["err_rate"]["currt"] * 100 * 100) / 100
      )}%)&nbsp&nbsp&nbsp
      
      low error rate(${parseInt(
        (info_data["err_rate"]["low"] * 100 * 100) / 100
      )}%)
      
      </p>
      <div>
        <h2 style="color:rgba(97, 104, 124, 1); font-size: 1.2rem;"> the result of the graph</h2>
        <img style= 'width:15rem' src="/static/${info_data["graph"][0]}">
        <img style= 'width:15rem' src="/static/${info_data["graph"][1]}">
      </div>
      `;
      document.getElementById("anal_data").innerHTML = ghtml;
      console.log(today_str);
      // data[0] current
      // data[1] highest
      // data[2] lowest

      for (let data of info_data["y_pred"]) {
        inHtml += `<div style='padding:0.5rem; border:2px solid darkgray; margin-bottom:1rem'>
        <p style='padding:0.5rem; background: rgba(139, 161, 182, 1)'>
        ${today_str} </p>
        <p style='color:red'>the highest price : ${data[1]}</p>
        <p>the current price : ${data[0]}</p>
        <p style='color:blue'>the lowest price : ${data[2]}</p>
        </div>
      `;
        today_date.setDate(today_date.getDate() + 1);
        today_str = today_date.toLocaleDateString("ko-kr");
      }
    }
    document.getElementById("result").innerHTML = inHtml;
    res_contain.style.display = "block";
  });
}
