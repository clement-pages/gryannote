import gradio as gr
from gryannote_pipeline import PipelineSelector


def update_token(oauth_token: gr.OAuthToken | None = None):
    token = oauth_token.token if oauth_token else None
    return PipelineSelector(show_config=True, token=token)


with gr.Blocks() as demo:
    login_button = gr.LoginButton()
    pipeline_selector = PipelineSelector(show_config=True)

    pipeline_selector.select(
        fn=pipeline_selector.on_select,
        inputs=pipeline_selector,
        outputs=pipeline_selector,
        preprocess=False,
        postprocess=False,
    )
    pipeline_selector.change(
        fn=pipeline_selector.on_change,
        inputs=pipeline_selector,
        outputs=pipeline_selector,
        preprocess=False,
        postprocess=False,
    )

    demo.load(update_token, inputs=None, outputs=pipeline_selector)


if __name__ == "__main__":
    demo.launch()
