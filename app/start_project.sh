SESSION="task-manager-fastapi"
PROJECT_DIR=~/task-manager-fastapi
VENV_PATH="$PROJECT_DIR/venv2/bin/activate"

#check if session exists
tmux has-session -t $SESSION 2>/dev/null

if [ $? != 0 ]; then 
    tmux set-option -g mouse on
    tmux new-session -d -s $SESSION -n "postgres"
    tmux send-keys -t $SESSION:postgres "psql -h localhost -U postgres tasktracker_db" C-m

    #pane 1 
    tmux set-option -g mouse on
    tmux split-window -v -t $SESSION
    tmux send-keys -t $SESSION "cd $PROJECT_DIR" C-m
    tmux send-keys -t $SESSION "source $VENV_PATH" C-m
    tmux send-keys -t $SESSION "uvicorn app.main:app --reload" C-m
    
    #pane 2
    tmux set-option -g mouse on
    tmux split-window -h -t $SESSION
    tmux send-keys -t $SESSION "cd $PROJECT_DIR" C-m
    tmux send-keys -t $SESSION "source $VENV_PATH" C-m
    tmux send-keys -t $SESSION "celery -A app.core.celery_worker.celery_app worker --loglevel=info" C-m

fi

# #windows 0: Start postgresql
# tmux rename-window -t $SESSION:0 'postgres'
# tmux send-keys -t $SESSION:0  "cd $PROJECT_DIR" C-m
# tmux send-keys -t $SESSION:0 "source $VENV_PATH" C-m

#     #windows 1: Fastapiserever
#     tmux new-window -t $SESSION:1 'FastAPI'
#     tmux send-keys -t $SESSION:1  "cd $PROJECT_DIR" C-m
#     tmux send-keys -t $SESSION:1 "source $VENV_PATH" C-m

 #windows 2
    # tmux new-window -t $SESSION -n 'celery'
    # tmux send-keys -t $SESSION:celery  "cd $PROJECT_DIR" C-m
    # tmux send-keys -t $SESSION:celery "source $VENV_PATH" C-m
    # tmux send-keys -t $SESSION:celery "celery -A app.core.celery_worker.celery_app worker --loglevel=info" C-m