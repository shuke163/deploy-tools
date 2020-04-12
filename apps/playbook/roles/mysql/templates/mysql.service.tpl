[Unit]
Description=MySQL Server
After=syslog.target
After=network.target

[Service]
Type=simple
PermissionsStartOnly=true
ExecStartPre=/bin/chown {{ mysql_run_user }}:{{ mysql_run_user }} -R {{ mysql_datadir }} {{ base_path }}/mysql/data
ExecStart={{ mysql_path }}/bin/mysqld --datadir={{ mysql_datadir }} --log-error={{ mysql_log_error }} --pid-file={{ mysql_pid_file }} --socket={{ mysql_socket}} --port={{ mysql_port }}
TimeoutSec=300
LimitNOFILE=10240
PrivateTmp=true
User=mysql
Group=mysql
WorkingDirectory=/tmp/

[Install]
WantedBy=multi-user.target
