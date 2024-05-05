from typing import Awaitable, Callable, TypeVar, cast
import flet as ft

VERSION = "1.0.0"

editor_content = ft.TextField(multiline=True)


def SidebarFile(name: str, on_click: Callable[[ft.ControlEvent], Awaitable[None]]):
    button = ft.FilledButton("Open", on_click=on_click)
    button.data = name
    return ft.Container(
        ft.Row(
            [
                ft.Icon(ft.icons.EDIT_DOCUMENT),
                ft.Text(name),
                ft.Container(
                    bgcolor=ft.colors.RED,
                    width=20,
                ),
                button,
            ]
        ),
        bgcolor=ft.colors.SURFACE_VARIANT,
        padding=15,
        border_radius=12,
    )


async def main(page: ft.Page):
    page.title = f"Material Code Editor {VERSION}"
    opened_file_text = ft.Text()

    async def open_file(event: ft.ControlEvent):
        control = cast(ft.FilledButton, event.control)
        # print(control.data)
        editor_content.read_only = False
        opened_file_text.value = control.data
        try:
            f = open(control.data)
            editor_content.value = f.read()
            f.close()
        except OSError as e:
            editor_content.value = f"Error while trying to load file: {e}"
            editor_content.read_only = True
        await editor_content.update_async()
        await opened_file_text.update_async()

    async def save(_):
        if editor_content.value is None:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Saving"),
                content=ft.Text("Failed to save data: editor_content.value is None"),
            )
            page.dialog.open = True
            await page.update_async()
            return
        if opened_file_text.value is None:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Saving"),
                content=ft.Text("Failed to save data: no files open"),
            )
            page.dialog.open = True
            await page.update_async()
            return
        f = open(opened_file_text.value, "w+")
        f.write(editor_content.value)
        f.close()
        page.snack_bar = ft.SnackBar(
            ft.Row(
                [
                    ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN_ACCENT),
                    ft.Text("Saved!"),
                ]
            )
        )
        page.snack_bar.open = True
        await page.update_async()

    async def route_change(route: ft.RouteChangeEvent):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Card(
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            SidebarFile("D:/MCE/test.txt", open_file),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            )
                        ),
                        expand=True,
                        width=275,
                    ),
                    editor_content,
                ],
                ft.AppBar(
                    title=opened_file_text,
                    actions=[
                        ft.IconButton(
                            ft.icons.SAVE, on_click=save, tooltip="Save current file"
                        )
                    ],
                ),
            )
        )

        await page.update_async()

    async def view_pop(_):
        page.views.pop()
        top_view = page.views[-1]
        await page.go_async(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    await page.go_async(page.route)


ft.app(main, f"Material Code Editor {VERSION}")
