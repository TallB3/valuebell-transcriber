"""
Gradio interface for Valuebell Transcriber
"""
import gradio as gr
from config.settings import SUPPORTED_LANGUAGES, ALL_SUPPORTED_EXTENSIONS


def create_interface(process_function, download_function, clear_function):
    """Create the Gradio interface"""
    with gr.Blocks(title="Valuebell Transcriber", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🔔 Valuebell Transcriber")
        gr.Markdown("*Upload your audio or video files to get accurate transcripts with automatic speaker detection. Perfect for podcasts, interviews, and meetings.*")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## ⚙️ Settings")

                episode_name = gr.Textbox(
                    label="Episode Name",
                    placeholder="e.g., episode_01_interview_tech",
                    info="Use only letters, numbers, underscore, and dash"
                )

                source_type = gr.Radio(
                    choices=["Video File", "Audio File", "JSON Transcript"],
                    label="Source File Type",
                    value="Audio File",
                    info="What type of file are you uploading?"
                )

                delivery_method = gr.Radio(
                    choices=["File Upload", "URL"],
                    label="How to provide your file?",
                    value="File Upload"
                )

            with gr.Column(scale=1):
                gr.Markdown("## 🌐 Language & API")

                language = gr.Dropdown(
                    choices=SUPPORTED_LANGUAGES,
                    label="Language",
                    value="heb",
                    info="Select the primary language of your podcast"
                )

                api_key = gr.Textbox(
                    label="ElevenLabs API Key",
                    type="password",
                    placeholder="Enter your API key here",
                    info="Required for video/audio transcription"
                )

        with gr.Row():
            with gr.Column():
                file_input = gr.File(
                    label="Upload File",
                    file_types=ALL_SUPPORTED_EXTENSIONS,
                    visible=True
                )

                url_input = gr.Textbox(
                    label="File URL",
                    placeholder="https://drive.google.com/... or https://dropbox.com/...",
                    visible=False,
                    info="Supports Google Drive, Dropbox, WeTransfer"
                )

        # Show/hide inputs based on delivery method
        def update_inputs(delivery_method):
            if delivery_method == "File Upload":
                return gr.update(visible=True), gr.update(visible=False)
            else:
                return gr.update(visible=False), gr.update(visible=True)

        delivery_method.change(
            fn=update_inputs,
            inputs=[delivery_method],
            outputs=[file_input, url_input]
        )

        with gr.Row():
            process_btn = gr.Button("🚀 Start Processing", variant="primary", size="lg")
            clear_btn = gr.Button("🗑️ Clear All", variant="secondary")

        with gr.Row():
            with gr.Column():
                status_output = gr.Textbox(
                    label="Status",
                    lines=15,
                    interactive=False
                )

        with gr.Tabs():
            with gr.TabItem("📝 TXT Transcript"):
                txt_output = gr.Textbox(
                    label="TXT Transcript",
                    lines=15,
                    interactive=False,
                    show_copy_button=True
                )

            with gr.TabItem("📺 SRT Subtitles"):
                srt_output = gr.Textbox(
                    label="SRT Subtitles",
                    lines=15,
                    interactive=False,
                    show_copy_button=True
                )

            with gr.TabItem("💾 JSON Data"):
                json_output = gr.Textbox(
                    label="Raw JSON Data",
                    lines=15,
                    interactive=False,
                    show_copy_button=True
                )

        # Download selection section
        gr.Markdown("## 📥 Download Files")
        gr.Markdown("*Select files → Click 'Prepare Download' → Click the download link that appears*")

        with gr.Row():
            txt_checkbox = gr.Checkbox(label="📝 Transcript (.txt)", value=True)  # Selected by default
            srt_checkbox = gr.Checkbox(label="📺 Subtitles (.srt)", value=False)
            audio_checkbox = gr.Checkbox(label="🎵 Audio (.wav/.mp3)", value=False)
            json_checkbox = gr.Checkbox(label="💾 Raw Data (.json)", value=False)

        with gr.Row():
            download_btn = gr.Button("📦 Prepare Download", variant="primary", size="lg")

        with gr.Row():
            download_status = gr.Textbox(label="Step 2: Click the download link below", lines=2, interactive=False)

        with gr.Row():
            download_file = gr.File(label="⬇️ Click here to download your files", interactive=False)

        # Hidden components to store file paths
        txt_path_store = gr.State()
        srt_path_store = gr.State()
        audio_path_store = gr.State()
        json_path_store = gr.State()

        # Event handlers
        process_btn.click(
            fn=process_function,
            inputs=[
                episode_name,
                source_type,
                delivery_method,
                file_input,
                url_input,
                language,
                api_key
            ],
            outputs=[status_output, txt_output, srt_output, json_output, txt_path_store, srt_path_store, audio_path_store, json_path_store],
            show_progress=True
        )

        download_btn.click(
            fn=download_function,
            inputs=[
                txt_checkbox, srt_checkbox, audio_checkbox, json_checkbox,
                txt_path_store, srt_path_store, audio_path_store, json_path_store,
                episode_name
            ],
            outputs=[download_file, download_status]
        )

        clear_btn.click(
            fn=clear_function,
            outputs=[
                episode_name, source_type, delivery_method, file_input,
                url_input, language, api_key, status_output, txt_output, srt_output, json_output,
                txt_path_store, srt_path_store, audio_path_store, json_path_store, download_status, download_file
            ]
        )

    return interface


def get_clear_function():
    """Return the clear function for resetting all inputs"""
    def clear_all():
        return ("", "Audio File", "File Upload", None, "", "heb", "", "", "", "", "", None, None, None, None, "", None)

    return clear_all