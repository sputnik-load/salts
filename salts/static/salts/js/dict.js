var Lang = function() {
	var dictRu = {
		auth: {
			title: "нагрузочные тесты, результаты, графики",
			user_name: "Имя пользователя",
			password: "Пароль",
			exit_ok: "Вы успешно вышли",
			login_fail: "Неверное имя пользователя или пароль. " +
						"Проверьте правильность введённых данных.",
			login_but: "Войти",
			user_label: "Пользователь",
			exit: "Выйти"
		},
		menu: {
			run: "Запуск",
			results: "Результаты",
			tanks: "Танки",
			cms: "CMS"
		},
		run_page: {
			title: "запуск тестов",
			run_table: {
				title: "Запущенные тесты",	
				columns: {
					shooting_id: "ID стрельбы",
					id: "ID",
					test_name: "Имя теста",
					tank_host: "Имя хоста",
					action: "Действие",
					status: "Статус"
				}
			},
			avail_table: {
				title: "Доступные тесты",
				columns: {
					id: "ID",
					test_name: "Имя теста",
					tank_host: "Имя хоста",
					action: "Действие",
					status: "Статус"
				}
			},
			test_name: {
				name: "Имя теста",
				config_editor: {
					title: "Редактирование параметров сценария",
					test_name: "Имя теста",
					label: "Шаг",
					load_param_title: "Профиль нагрузки",
					load: {
						param_title: "Параметры",
						no: {
							desc: "добавить новую схему нагрузки"
						},
						line: {
							desc: "линейная нагрузка от {a} до {b} rps",
							a: "От",
							b: "До",
							dur: "Длительность"
						},
						const: {
							desc: "постоянная нагрузка {a} rps",
							a: "RPS",
							dur: "Длительность"
						},
						step: {
							desc: "ступенчатая нагрузка от {a} до {b} rps",
							a: "От",
							b: "До",
							step_rps: "Шаг",
							step_dur: "Длительность 1-го шага"
						}
					},
					target_title: "Цель",
					target: {
						hostname: "Имя хоста",
						port: "Порт",
					}
				},
				select_schedule: {
					options: {
						no: "Добавить новую схему нагрузки",
						line: "Линейная нагрузка",
						const: "Постоянная нагрузка",
						step: "Ступенчатая нагрузка"
					}
				}
			},
			tank_host: {
				no_tanks: "Нет доступных танков"
			},
			action: {
				run_but: "Запустить",
				stop_but: "Остановить"
			},
			status: {
				no_results: "Нет результатов.",
				info: "Последний тест {id} был завершён {date}.",
				run: "Выполняется тест. ID сессии - {session}. " +
					 "Запущен {date} пользователем {user}. " +
					 "Осталось - {remained}.",
				error: {
					"title": "Ошибка: ",
					"default": "неизвестная ошибка (имя ошибки {name})",
					"no_load_gen": "генератор нагрузки не объявлен " +
								   "в конфигурационном файле {scenario_path}",
					"section_need": "в конфигурационном файле {scenario_path} " +
								    "требуется секция '{section}'"
				}
			},
		},
		results_page: {
			title: "результаты тестов",
			table: {
				title: "Результаты тестов",
				columns: {
					id: "ID",
					test_name: "Тест",
					user: "Пользователь",
					test_status: "Статус",
					scenario_id: "Сценарий",
					target: "Цель",
					version: "Версия",
					rps: "RPS",
					q99: "99%",
					q90: "90%",
					q50: "50%",
					http_net: "Ошибки",
					duration: "Длительность",
					dt_finish: "Окончание",
					graph_url: "Графики",
					generator: "Генератор",
					test_id: "ID теста",
					ticket_id: "Задача",
					comment: "Комментарий"
				}
			},
			help: "Помощь",
			dynamics: {
				link: "Динамика результатов",
				title: "Графики трендов времён отклика"
			}
		},
		tanks_page: {
			title: "мониторинг танков",
			table: {
				title: "Мониторинг танков",
				columns: {
					id: "ID",
					host: "Хост",
					username: "Пользователь",
					scenario_name: "Сценарий",
					status: "Статус",
					countdown: "Осталось",
					ticket_url: "Тикет",
					webconsole: "WEB-консоль",
					test_result: "Результат теста"
				}
			},
			status: {
				choices: {
					starting: "Готовится к старту",
					interrupted: "Прерван",
					running: "Выполняется",
					finished: "Закончен"
				}
			}
		}
	};
	var dictEn = {
		auth: {
			title: "load tests, results, graphs",
			user_name: "User Name",
			password: "Password",
			exit_ok: "You have successfully logged out",
			login_fail: "The username or password you entered " +
					    "is incorrect. Check the entered data.",
			login_but: "Log in",
			user_label: "User",
			exit: "Logout"
		},
		menu: {
			run: "Run",
			results: "Results",
			tanks: "Tanks",
			cms: "CMS"
		},
		run_page: {
			title: "tests run",
			run_table: {
				title: "Running Tests",	
				columns: {
					shooting_id: "Shooting ID",
					id: "ID",
					test_name: "Test Name",
					tank_host: "Host Name",
					action: "Action",
					status: "Status"
				}
			},
			avail_table: {
				title: "Available Tests",
				columns: {
					id: "ID",
					test_name: "Test Name",
					tank_host: "Host Name",
					action: "Action",
					status: "Status"
				}
			},
			test_name: {
				name: "Test Name",
				config_editor: {
					title: "Scenario Parameters Edit",
					test_name: "Test Name",
					label: "Step",
					load_param_title: "RPS Schedule",
					load: {
						param_title: "Parameters",
						no: {
							desc: "select to add new scheme"
						},
						line: {
							desc: "linear load from {a} to {b} rps",
							a: "From",
							b: "To",
							dur: "Duration"
						},
						const: {
							desc: "const load for {a} rps",
							a: "RPS",
							dur: "Duration"
						},
						step: {
							desc: "step load from {a} to {b} rps",
							a: "From",
							b: "To",
							step_rps: "Step",
							step_dur: "Duration for one step"
						}
					},
					target_title: "Target",
					target: {
						hostname: "Host Name",
						port: "Port",
					}
				},
				select_schedule: {
					options: {
						no: "Select To Add New Scheme",
						line: "Linear Load",
						const: "Constant Load",
						step: "Stepped Load"
					}
				}
			},
			tank_host: {
				no_tanks: "No available tanks"
			},
			action: {
				run_but: "Run",
				stop_but: "Stop"
			},
			status: {
				no_results: "No results.",
				info: "The final test {id} was completed {date}.",
				run: "The test is running. Session ID is {session}. " +
					 "The test started {date} by {user}. Remained time is " +
					 "{remained}.",
				error: {
					"title": "Error: ",
					"default": "unknown error (the name of error - {name})",
					"no_load_gen": "the load generator not declared in " +
								   "the {scenario_path} config",
					"section_need": "the '{section}' section is required " +
								    "in the {scenario_path} config"
				}
			}	
		},
		results_page: {
			title: "results of tests",
			table: {
				title: "Test Results",
				columns: {
					id: "ID",
					test_name: "Test",
					user: "User",
					test_status: "Status",
					scenario_id: "Scenario",
					target: "Target",
					version: "Version",
					rps: "RPS",
					q99: "99%",
					q90: "90%",
					q50: "50%",
					http_net: "Errors",
					duration: "Duration",
					dt_finish: "Finish",
					graph_url: "Graphs",
					generator: "Generator",
					test_id: "Test ID",
					ticket_id: "Task",
					comment: "Comment"
				}
			},
			help: "Help",
			dynamics: {
				link: "Results Dynamics",
				title: "Quantile trends response times"
			}
		},
		tanks_page: {
			title: "tanks monitoring",
			table: {
				title: "Tanks Monitoring",
				columns: {
					id: "ID",
					host: "Host",
					username: "User",
					scenario_name: "Scenario",
					status: "Status",
					countdown: "Remained",
					ticket_url: "Ticket",
					webconsole: "WEB-console",
					test_result: "Test Result"
				}
			},
			status: {
				choices: {
					starting: "Starting",
					interrupted: "Interrupted",
					running: "Running",
					finished: "Finished"
				}
			}
		}	
	};

	var locales = {
		"ru-RU": dictRu,
		"en-US": dictEn
	};
	var currentLocale = "ru-RU";
	return {
		tr: locales[currentLocale],
		current: currentLocale
	}
}()
