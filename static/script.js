function copy(id, button) {

    const element = document.getElementById(id);

    if (!element) return;

    const text = element.innerText.trim();

    navigator.clipboard.writeText(text);

    const original = button.innerText;

    button.innerText = "Copied!";

    button.disabled = true;

    setTimeout(() => {

        button.innerText = original;

        button.disabled = false;

    }, 1200);
}


window.onload = function () {

    const input =
        document.getElementById("fileInput");

    const output =
        document.getElementById("result");

    const dropzone =
        document.querySelector(".dropzone");

    if (!input) {
        console.log("Input not found");
        return;
    }

    input.onchange = async function () {

        if (input.files.length === 0) {
            return;
        }

        const file = input.files[0];

        if (
            !file.name
                .toLowerCase()
                .endsWith(".dem")
        ) {

            alert("Select a .dem file");

            input.value = "";

            return;
        }

        // Loading state

        dropzone.innerHTML = `
            <div class="drop-title">
                Processing...
            </div>

            <div class="drop-sub">
                Parsing demo
            </div>
        `;

        const formData = new FormData();

        formData.append(
            "demo",
            file
        );

        try {

            const response =
                await fetch("/parse", {

                    method: "POST",

                    body: formData
                });

            const html =
                await response.text();

            output.innerHTML = html;

        } catch (error) {

            console.error(error);

            output.innerHTML = `
                <div class="error">
                    Upload failed
                </div>
            `;
        }

        // Restore dropzone

        dropzone.innerHTML = `
            <div class="drop-title">
                Drop your demo file here
            </div>

            <div class="drop-sub">
                or click to browse (.dem)
            </div>
        `;

        // Reset input

        input.value = "";
    };
};