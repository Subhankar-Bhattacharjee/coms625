
        set logging file trace_3.log
        set logging on

        break main
        run 3 2 1

        define step_and_log_ir
        while ($pc != 0)
            if ($pc == 0)
                break
            end
            x/i $pc
            stepi
        end
        end

        step_and_log_ir

        set logging off
        quit
    