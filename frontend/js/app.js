let chart = null;

const input = document.getElementById("q");

input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        askQuestion();
    }
});

async function uploadCSV() {

    const fileInput =
        document.getElementById(
            "csvFile"
        );

    const uploadStatus =
        document.getElementById(
            "uploadStatus"
        );

    if (!fileInput.files.length) {

        uploadStatus.innerHTML = `
            <div class="error-box">
                Please select a CSV file.
            </div>
        `;

        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        fileInput.files[0]
    );

    uploadStatus.innerHTML = `
        <div class="status-box">
            Uploading dataset...
        </div>
    `;

    try {

        const response =
            await fetch(
                "http://localhost:8000/upload-csv",
                {
                    method: "POST",
                    body: formData
                }
            );

        const data =
            await response.json();

        if (response.ok) {

            uploadStatus.innerHTML = `
                <div class="success-box">

                    <h3>
                        ✅ CSV Uploaded Successfully
                    </h3>

                    <p>
                        <strong>Table:</strong>
                        ${data.table}
                    </p>

                    <p>
                        <strong>Rows:</strong>
                        ${data.rows}
                    </p>

                    <p>
                        <strong>Columns:</strong>
                        ${data.columns.length}
                    </p>

                    <p>
                        <strong>Detected Fields:</strong>
                        <br>
                        ${data.columns.join(", ")}
                    </p>

                </div>
            `;

        } else {

            uploadStatus.innerHTML = `
                <div class="error-box">
                    ❌ ${data.detail}
                </div>
            `;
        }

    } catch (error) {

        console.error(error);

        uploadStatus.innerHTML = `
            <div class="error-box">
                ❌ Could not connect to FastAPI server.
            </div>
        `;
    }
}

async function askQuestion() {

    const question =
        input.value.trim();

    if (!question) return;

    const output =
        document.getElementById(
            "out"
        );

    const btn =
        document.getElementById(
            "btn"
        );

    btn.disabled = true;

    if (chart) {

        chart.destroy();

        chart = null;
    }

    output.innerHTML = `
        <div class="card">
            <div class="card-body status">
                Generating SQL, insights and charts...
            </div>
        </div>
    `;

    try {

        const response =
            await fetch(
                "http://localhost:8000/query",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        question: question
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            output.innerHTML = `
                <div class="card">
                    <div class="card-body error">
                        ${data.detail}
                    </div>
                </div>
            `;

            return;
        }

        let html = "";

        html += `
            <div class="card">
                <div class="card-header">
                    Generated SQL
                </div>

                <div class="card-body">
                    <pre class="sql">${data.sql}</pre>
                </div>
            </div>
        `;

        if (
            data.insights &&
            data.insights.length > 0
        ) {

            html += `
                <div class="card">
                    <div class="card-header">
                        AI Insights
                    </div>

                    <div class="card-body">
            `;

            data.insights.forEach(
                (
                    insight,
                    index
                ) => {

                    html += `
                        <div class="insight">
                            <strong>
                                ${index + 1}.
                            </strong>
                            ${insight}
                        </div>
                    `;
                }
            );

            html += `
                    </div>
                </div>
            `;
        }

        if (
            data.result.success
        ) {

            const cols =
                data.result.columns;

            const rows =
                data.result.rows;

            html += `
                <div class="card">
                    <div class="card-header">
                        Results (${rows.length} rows)
                    </div>

                    <div class="card-body">
            `;

            if (
                rows.length > 0
            ) {

                html += `
                    <div class="table-container">

                    <table>

                        <thead>
                            <tr>

                                ${cols.map(
                                    col =>
                                        `<th>${col}</th>`
                                ).join("")}

                            </tr>
                        </thead>

                        <tbody>
                `;

                rows.forEach(
                    row => {

                        html += `
                            <tr>

                            ${cols.map(
                                col =>
                                    `<td>${row[col] ?? ""}</td>`
                            ).join("")}

                            </tr>
                        `;
                    }
                );

                html += `
                        </tbody>

                    </table>

                    </div>
                `;

            } else {

                html += `
                    <p>
                        No rows returned.
                    </p>
                `;
            }

            html += `
                    </div>
                </div>
            `;
        }

        if (
            data.chart &&
            data.chart.chartable &&
            data.result.rows.length > 0
        ) {

            html += `
                <div class="card">

                    <div class="card-header">
                        ${data.chart.title}
                    </div>

                    <div class="card-body">

                        <div class="chart-container">
                            <canvas id="chartCanvas"></canvas>
                        </div>

                    </div>

                </div>
            `;
        }

        output.innerHTML = html;

        if (
            data.chart &&
            data.chart.chartable &&
            data.result.rows.length > 0
        ) {

            const labels =
                data.result.rows.map(
                    row =>
                        String(
                            row[
                                data.chart.x
                            ]
                        )
                );

            const values =
                data.result.rows.map(
                    row =>
                        Number(
                            row[
                                data.chart.y
                            ]
                        )
                );

            chart = new Chart(
                document.getElementById(
                    "chartCanvas"
                ),
                {
                    type:
                        data.chart.type,

                    data: {

                        labels:

                            labels,

                        datasets: [
                            {
                                label:
                                    data.chart.y,

                                data:
                                    values,

                                borderWidth:
                                    2
                            }
                        ]
                    },

                    options: {

                        responsive:
                            true,

                        maintainAspectRatio:
                            false,

                        plugins: {

                            legend: {
                                display: true
                            }
                        }
                    }
                }
            );
        }

        input.value = "";

    } catch (error) {

        console.error(
            error
        );

        output.innerHTML = `
            <div class="card">

                <div class="card-body error">

                    Could not connect to FastAPI server.

                </div>

            </div>
        `;
    }

    btn.disabled = false;
}