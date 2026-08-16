# ================================
# ZSH HISTORY + EXECUTION LOGGING
# ================================

# History file
export HISTFILE="$HOME/.zsh_history"
export HISTSIZE=100000
export SAVEHIST=100000

# History behavior
setopt appendhistory
setopt extendedhistory
setopt sharehistory
setopt incappendhistory
setopt histignorealldups
setopt histignorespace

# Execution logger (forensics-grade)
preexec() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $(pwd) | $1" >> "$HOME/.exec.log"
}
setopt NO_HIST_EXPAND
setopt NO_BANG_HIST
[[ -f ~/.sync-termux.sh ]] && ~/.sync-termux.sh
