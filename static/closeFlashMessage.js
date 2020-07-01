function closeFlashMessage() {
	const msg_box = document.getElementById("flash-message-box");
	if (msg_box) {
		setTimeout(function () {
			document.getElementById("flash-message-box").style.display = "none";
			console.log("closed!");
		}, 3000);
	}
}