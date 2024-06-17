class VersionInfo:
	version = '4.6.0'
	description = {
		'4.6.0': '''
・新たに以下の機能を実装しています:
　・`Walica`モジュール
　　・割り勘イベント作成・確認・削除
　　　- `/add-event`, `/view-event`, `/remove-event`
　　・割り勘項目作成・確認・削除
　　　- `/add-item`, `/view-item`, `/remove-item`
　　・自分の支払いを確認
　　　- `/view-payment`
''',
		'4.5.0': '''
・以下のサービスに対応しました:
　・GitHub (https://github.com/Tateshiki0529/VABot)
''',
		'4.4.2': '''
・新たに以下の機能を実装しています:
　・`Math`モジュール
　　・素数判定コマンド
　　　- `/prime`
''',
		'4.4.1': '''
・新たに以下の機能を実装しています:
　・`Trolls`モジュール
　　・5000兆円欲しいコマンド
　　　- `/5000000000000000`
''',
		'4.4.0': '''
・新たに以下の機能を実装しています:
　・`TrainInfo`モジュール
　　・近くの路線の運行状況確認コマンド
　　　- `/traininfo`
　　・すべての路線の運行状況確認コマンド
　　　- `/traininfo-local`
''',
		'4.3.0': '''
・新たに以下の機能を実装しています:
　・`Gomamayo`モジュール
　　・ゴママヨ判定コマンド (一部ゴママヨ非対応)
　　　- `/gomamayo`
　　・ゴママヨ判定システム
　　　- 会話にゴママヨが認められるとリアクションをとります
・以下の機能は開発を保留しています:
　・`Gomamayo`モジュール
　　・ゴママヨ判定機能 (完全)
''',
		'4.2.1': '''
・新たに以下の機能を(一部)実装しています:
　・`Gomamayo`モジュール
　　・ゴママヨ判定コマンド (バニラゴママヨのみ対応)
　　　- `/gomamayo`
・以下の機能が開発中です:
　・`Gomamayo`モジュール
　　・ゴママヨ判定機能
''',
		'4.2.0': '''
・新たに以下の機能を実装しています:
　・`Trolls`モジュール
　　・なんでまだ実装してるのかわからないコマンド群
　　　- `/troll`
　　　- `/fucks`
　　　- `/yesno`
''',
		'4.1.0': '''
・新たに以下の機能を実装しています:
　・`Images`モジュール
　　・画像登録・編集コマンド
　　　- `/image-edit`
　　・画像召喚コマンド
　　　- `/im`
''',
		'4.0.0': '''
・コードの書き直しを行いました
・Botの名称変更を行いました
・すべての機能を削除し、新たに以下の機能を実装しています:
　・`Core`モジュール
　　・バージョン情報コマンド
　　　- `/version`
　・`Debug`モジュール
　　・変数確認コマンド
　　　- `/view-variables`
'''
	}