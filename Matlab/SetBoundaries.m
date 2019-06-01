%%
% Function keeping the output value of inputted enexpectable
% function in the specified boundaries
% @param MinVal: minimum output value
% @param MaxVal: maximum output value
% @param Func: the function we want to limit
% @return: the same function that was inputted with boundaries on its output
function R=SetBoundaries(MinVal,MaxVal,Func)
    R=max(MinVal,min(MaxVal,Func));
endfunction
