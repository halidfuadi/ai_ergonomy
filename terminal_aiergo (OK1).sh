#!/bin/bash
gnome-terminal --title="BACKEND" --command="bash -i backend_script.sh"
gnome-terminal --title="FRONTEND" --command="bash -i frontend_script.sh"
google-chrome --new-window http://localhost:3000/img
