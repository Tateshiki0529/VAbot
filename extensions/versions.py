class VersionInfo:
	version = '4.10.0'
	description = {
		'4.11.0': '''
・システム構造を更新しました:
　・モジュール読み込みシステムからエクステンション読み込みシステムに更新
　　- ホットリロードに対応
''',
		'4.10.0': '''
・新たに以下の機能を実装しています:
　・`Trolls`モジュール
　　・114514変換コマンド from itorr/homo
　　　- `/homo`
''',
		'4.9.0': '''
・新たに以下の機能を実装しています:
　・`Music`モジュール
　　・音楽Bot(仮)機能
''',
		'4.8.3': '''
・以下の機能を修正しています:
　・`Debug`モジュール
　　・コードの一部最適化
''',
		'4.8.2': '''
・以下の機能を修正しています:
　・`VOICEVOX`モジュール, `Voice`モジュール
　　・コードの一部最適化
''',
		'4.8.1': '''
・新たに以下の機能を実装しています:
　・`VOICEVOX`モジュール
　　・文字読み上げ機能(仮)
　　　- `/tts-vv`
''',
		'4.8.0': '''
・新たに以下の機能を実装しています:
　・`VOICEVOX`モジュール
　　・音声合成コマンド
　　　- `/make-voice`
''',
		'4.7.0': '''
・新たに以下の機能を実装しています:
　・`Voice`モジュール
　　・通話専用チャット機能
　　　- `/call-channel`
''',
		'4.6.2': '''
・新たに以下の機能を実装しています:
　・`Weather`モジュール
　　・天気通知機能(仮)
''',
		'4.6.1': '''
・新たに以下の機能を実装しています:
　・`Weather`モジュール
　　・現在地取得テストコマンド
　　　- `/get-location`
''',
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