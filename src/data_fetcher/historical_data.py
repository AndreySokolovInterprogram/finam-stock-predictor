    def _save_to_db(self, symbol, mic, timeframe, df):
        """Сохраняет свечи в БД по одной с обработкой ошибок."""
        session = get_db_session()
        saved = 0
        try:
            ticker = session.query(Ticker).filter_by(symbol=symbol, exchange=mic).first()
            if not ticker:
                ticker = Ticker(symbol=symbol, name=symbol, exchange=mic)
                session.add(ticker)
                session.commit()
            
            for idx, row in df.iterrows():
                try:
                    candle_time = pd.to_datetime(str(idx)).to_pydatetime().replace(tzinfo=None)
                    candle = Candle(
                        ticker_id=ticker.id,
                        timeframe=timeframe,
                        open_price=float(row["open"]),
                        high_price=float(row["high"]),
                        low_price=float(row["low"]),
                        close_price=float(row["close"]),
                        volume=int(float(row["volume"])),
                        candle_time=candle_time,
                    )
                    session.add(candle)
                    session.commit()
                    saved += 1
                except Exception as e:
                    session.rollback()
                    logger.warning(f"Skip candle {idx}: {e}")
                    continue
            
            logger.info(f"Saved {saved}/{len(df)} candles for {symbol}")
        except Exception as e:
            session.rollback()
            logger.error(f"DB error: {e}")
        finally:
            session.close()